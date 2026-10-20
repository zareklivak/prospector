"""
Pipeline orchestrator - manages execution of Phase 1/2/3
"""
import sys
import os
import asyncio
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
import pandas as pd

from backend_api.config import (
    OUTPUT_DIR, PHASE1_DIR, PHASE2_DIR, PHASE3_DIR,
    TIME_PHASE1_PER_COMPANY, TIME_PHASE2_PER_CONTACT, TIME_PHASE3_PER_CONTACT
)
from backend_api.websocket_handler import manager
from backend_api.utils.cost_tracker import CostTracker


class PipelineOrchestrator:
    """Orchestrates the full 3-phase pipeline"""

    def __init__(self, job_id: str, config: Dict):
        """
        Args:
            job_id: Unique job identifier
            config: Pipeline configuration dictionary
        """
        self.job_id = job_id
        self.config = config
        self.cost_tracker = CostTracker()
        self.start_time = None
        self.status = "queued"
        self.current_stage = None
        self.error_message = None

        # Kill switch support
        self.cancelled = False
        self.current_process = None

        # Output file paths
        self.phase1_output = None
        self.phase2_output = None
        self.phase3_output = None

        # Metrics
        self.metrics = {
            "companies_total": len(config["company_domains"]),
            "companies_done": 0,
            "contacts_scraped": 0,
            "contacts_scraped_total": len(config["company_domains"]) * config["contacts_per_company"],
            "contacts_enriched": 0,
            "contacts_enriched_total": 0,
            "messages_generated": 0,
            "messages_generated_total": 0,
            "cost_estimated": 0.0,
            "cost_actual": 0.0,
            "time_elapsed_seconds": 0,
            "time_remaining_seconds": 0
        }

        # Estimate initial cost (accounts for mode and options)
        self.metrics["cost_estimated"] = CostTracker.estimate_cost(
            companies=len(config["company_domains"]),
            contacts_per_company=config["contacts_per_company"],
            enrich_emails=config.get("enrich_emails", True),
            prospect_only=config.get("prospect_only", False),
            skip_linkedin=config.get("skip_linkedin", False),
            waterfall_enrichment=config.get("waterfall_enrichment", False)
        )["total"]

    async def _run_subprocess_with_logs(self, cmd: list, cwd: str) -> subprocess.CompletedProcess:
        """
        Run a subprocess and stream its output to WebSocket in real-time

        Args:
            cmd: Command and arguments as list
            cwd: Working directory for the subprocess

        Returns:
            CompletedProcess object
        """
        # Force unbuffered Python output for immediate log streaming
        # This prevents logs from getting stuck in Python's stdout buffer
        if cmd[0] in ["python", "python3"]:
            cmd.insert(1, "-u")  # Add unbuffered flag

        # Set PYTHONUNBUFFERED environment variable as backup
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'

        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=env  # Use environment with PYTHONUNBUFFERED
        )

        # Store current process for kill switch
        self.current_process = process

        # Filter keywords for Apify noise
        apify_noise = ['apify', 'ACTOR', 'System info', 'Creating container', 'Pulling container', 'Starting container']

        # Stream output line by line
        while True:
            # Check for cancellation
            if self.cancelled:
                await self._send_log("🛑 Pipeline cancelled by user - terminating...", "warning")
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    await self._send_log("⚠️ Process didn't terminate gracefully, force killing...", "error")
                    process.kill()
                    await process.wait()

                return subprocess.CompletedProcess(
                    args=cmd,
                    returncode=-1,  # Indicate cancellation
                    stdout=None,
                    stderr=None
                )

            line = await process.stdout.readline()
            if not line:
                break

            decoded_line = line.decode('utf-8').rstrip()
            if decoded_line:
                # Filter out Apify verbose logging
                if not any(noise in decoded_line for noise in apify_noise):
                    await self._send_log(decoded_line, "info")

        # Wait for process to complete
        await process.wait()

        # Clear current process
        self.current_process = None

        return subprocess.CompletedProcess(
            args=cmd,
            returncode=process.returncode,
            stdout=None,
            stderr=None
        )

    async def run(self) -> str:
        """
        Run the full pipeline: Phase 1 → Phase 2 → Phase 3
        OR just Phase 1 if prospect_only=True

        Returns:
            Path to final output CSV
        """
        self.status = "running"
        self.start_time = time.time()

        try:
            prospect_only = self.config.get("prospect_only", False)

            if prospect_only:
                await self._send_log("🚀 Starting Prospector (Prospect-Only Mode)", "info")
            else:
                await self._send_log("🚀 Starting Prospector Pipeline", "info")

            await self._send_log(f"Companies: {len(self.config['company_domains'])}", "info")
            await self._send_log(f"Contacts per company: {self.config['contacts_per_company']}", "info")

            if not prospect_only:
                await self._send_log(f"Mode: {self.config['message_mode']}", "info")

            await self._send_log(f"Estimated cost: ${self.metrics['cost_estimated']:.2f}", "info")
            await self._send_log("", "info")

            # Phase 1: Apollo Scraping
            await self._run_phase1()

            # If prospect-only mode
            if prospect_only:
                enrich_emails = self.config.get("enrich_emails", False)

                # If email enrichment is enabled, run Phase 2 email-only (waterfall enrichment)
                if enrich_emails:
                    await self._send_log("", "info")
                    await self._send_log("📧 Running email enrichment for prospect-only mode...", "info")
                    await self._run_phase2_email_only()

                    self.status = "complete"
                    await self._send_log("", "info")
                    await self._send_log("✅ Prospect-only mode with email enrichment complete!", "success")
                    await self._send_log(f"Total cost: ${self.cost_tracker.get_total_cost():.2f}", "success")
                    await self._send_log(f"Output: {self.phase2_output}", "success")
                    await manager.send_complete(self.job_id, str(self.phase2_output))
                    return str(self.phase2_output)
                else:
                    # Standard prospect-only: just Phase 1 (no enrichment)
                    self.status = "complete"
                    await self._send_log("", "info")
                    await self._send_log("✅ Prospect-only mode complete!", "success")
                    await self._send_log(f"Total cost: ${self.cost_tracker.get_total_cost():.2f}", "success")
                    await self._send_log(f"Output: {self.phase1_output}", "success")
                    await manager.send_complete(self.job_id, str(self.phase1_output))
                    return str(self.phase1_output)

            # Phase 2: Enrichment
            await self._run_phase2()

            # Phase 3: Message Generation
            await self._run_phase3()

            # Complete
            self.status = "complete"
            await self._send_log("", "info")
            await self._send_log("✅ Pipeline complete!", "success")
            await self._send_log(f"Total cost: ${self.cost_tracker.get_total_cost():.2f}", "success")
            await self._send_log(f"Output: {self.phase3_output}", "success")

            await manager.send_complete(self.job_id, str(self.phase3_output))

            return str(self.phase3_output)

        except Exception as e:
            self.status = "error"
            self.error_message = str(e)
            await self._send_log(f"❌ Pipeline failed: {e}", "error")
            await manager.send_error(self.job_id, str(e))
            raise

    async def _run_phase1(self):
        """Run Phase 1: Apollo Scraping as subprocess"""
        import json
        self.current_stage = "phase1_apollo"
        await self._send_log("📋 PHASE 1: Apollo Scraping & Lead Scoring", "info")

        phase1_dir = Path(__file__).parent.parent / "phase1_apollo"

        # Prepare command
        cmd = [
            sys.executable,
            "run_phase1.py",
            json.dumps(self.config["company_domains"]),
            str(self.config["contacts_per_company"])
        ]

        # Email enrichment now happens in Phase 2 via waterfall (Apollo -> Hunter -> Findymail)
        prospect_only = self.config.get("prospect_only", False)
        enrich_emails = self.config.get("enrich_emails", False)

        # When enrich_emails is enabled OR include_unverified_contacts is enabled,
        # include all contacts (don't filter by email status in Apollo API)
        include_unverified = self.config.get("include_unverified_contacts", False)
        if enrich_emails or include_unverified:
            cmd.append("--include-all-contacts")
            if enrich_emails:
                await self._send_log("   Including all contacts for Phase 2 waterfall enrichment", "info")
            else:
                await self._send_log("   Including all contacts (LinkedIn-only mode)", "info")

        # Add seniorities if role_levels is specified
        role_levels = self.config.get("role_levels")
        if role_levels:
            seniorities = []
            if role_levels.get("c_suite", True):
                seniorities.extend(["c_suite", "head"])
            if role_levels.get("vp", True):
                seniorities.append("vp")
            if role_levels.get("director", True):
                seniorities.append("director")
            if role_levels.get("manager", False):
                seniorities.append("manager")

            if seniorities:
                cmd.extend(["--seniorities", json.dumps(seniorities)])
                await self._send_log(f"   Role levels: {', '.join(seniorities)}", "info")

        # Add max_initial_scrape if specified
        max_initial_scrape = self.config.get("max_initial_scrape", 2000)
        if max_initial_scrape != 2000:
            cmd.extend(["--max-initial-scrape", str(max_initial_scrape)])
            await self._send_log(f"   Max initial scrape: {max_initial_scrape}", "info")

        # Add min_score filter (applies BEFORE expensive operations like email enrichment)
        min_score = self.config.get("min_score", 1)
        if min_score > 1:
            cmd.extend(["--min-score", str(min_score)])
            await self._send_log(f"   Min ICP score filter: {min_score}+", "info")

        # Add include_unverified_contacts flag if set (for LinkedIn-only outreach)
        if include_unverified:
            cmd.append("--include-unverified")
            await self._send_log("   Including contacts without verified emails", "info")

        # Record start time to find only NEW output files
        import time as time_module
        phase1_start_time = time_module.time()

        # Run subprocess with log streaming
        result = await self._run_subprocess_with_logs(cmd, str(phase1_dir))

        if result.returncode != 0:
            raise RuntimeError(f"Phase 1 failed with return code {result.returncode}")

        # Find output path - only consider files created AFTER this run started
        output_dir = phase1_dir / "output"
        phase1_files = [
            f for f in output_dir.glob("phase1_ranked_contacts_*.csv")
            if f.stat().st_mtime >= phase1_start_time
        ]
        phase1_files = sorted(phase1_files, key=lambda p: p.stat().st_mtime, reverse=True)

        if not phase1_files:
            raise RuntimeError("Phase 1 completed but no contacts found matching your criteria. Try lowering the min ICP score or broadening your search.")

        self.phase1_output = str(phase1_files[0].absolute())

        # Update metrics
        df = pd.read_csv(self.phase1_output)
        self.metrics["contacts_scraped"] = len(df)
        self.metrics["contacts_enriched_total"] = len(df)
        self.metrics["messages_generated_total"] = len(df)
        self.metrics["companies_done"] = len(self.config["company_domains"])
        self.cost_tracker.add_phase1_cost(len(df))

        await self._update_metrics()
        await self._send_log(f"✓ Phase 1 complete: {len(df)} contacts scraped", "success")
        await self._send_log("", "info")

    async def _run_phase2(self):
        """Run Phase 2: Enrichment & Research as subprocess"""
        self.current_stage = "phase2_enrichment"
        await self._send_log("🔍 PHASE 2: Enrichment & Research", "info")

        phase2_dir = Path(__file__).parent.parent / "phase2_enrichment"

        # Prepare command
        cmd = [sys.executable, "run_phase2.py", self.phase1_output]

        # Email enrichment (Fast mode = Apollo only, Thorough mode = waterfall)
        if self.config.get("enrich_emails", True):
            cmd.append("--enrich-emails")
            if self.config.get("waterfall_enrichment", False):
                cmd.append("--waterfall")
                await self._send_log("   Email enrichment: Thorough mode (Apollo -> Hunter -> Findymail)", "info")
            else:
                await self._send_log("   Email enrichment: Fast mode (Apollo only)", "info")

        if self.config.get("verify_current_employment", False):
            cmd.append("--verify-employment")
            await self._send_log("   Employment verification enabled (LinkedIn)", "info")

        if self.config.get("skip_linkedin", False):
            cmd.append("--skip-linkedin")
            await self._send_log("   LinkedIn scraping disabled (using company research only)", "info")

        min_score = self.config.get("min_score", 1)
        cmd.extend(["--min-score", str(min_score)])

        # Pass min_profile_quality to Phase 2 (filters before company research to save API costs)
        min_profile_quality = self.config.get("min_profile_quality")
        if min_profile_quality and min_profile_quality > 1:
            cmd.extend(["--min-profile-quality", str(min_profile_quality)])
            await self._send_log(f"   Profile quality filter enabled (>= {min_profile_quality})", "info")

        # Run subprocess with log streaming
        result = await self._run_subprocess_with_logs(cmd, str(phase2_dir))

        if result.returncode != 0:
            raise RuntimeError(f"Phase 2 failed with return code {result.returncode}")

        # Find output path from file system
        output_dir = phase2_dir / "output"
        phase2_files = sorted(output_dir.glob("phase2_enriched_*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)

        if not phase2_files:
            raise RuntimeError("Phase 2 completed but no output CSV found")

        self.phase2_output = str(phase2_files[0].absolute())

        # Update metrics and costs
        df_enriched = pd.read_csv(self.phase2_output)
        self.metrics["contacts_enriched"] = len(df_enriched)

        # Track costs
        if self.config.get("enrich_emails", True):
            self.cost_tracker.add_phase2_email_cost(len(df_enriched))
        self.cost_tracker.add_phase2_linkedin_cost(len(df_enriched))
        self.cost_tracker.add_phase2_research_cost(len(self.config["company_domains"]))

        self.metrics["cost_actual"] = self.cost_tracker.get_total_cost()

        await self._update_metrics()
        await self._send_log(f"✓ Phase 2 complete: {len(df_enriched)} contacts enriched", "success")
        await self._send_log("", "info")

    async def _run_phase2_email_only(self):
        """
        Run Phase 2 with email enrichment only (skip LinkedIn and company research).
        Used for prospect-only mode with email enrichment enabled.
        """
        self.current_stage = "phase2_enrichment"
        await self._send_log("🔍 PHASE 2: Email Enrichment Only", "info")

        phase2_dir = Path(__file__).parent.parent / "phase2_enrichment"

        # Prepare command - email enrichment + skip LinkedIn and company research
        cmd = [sys.executable, "run_phase2.py", self.phase1_output]

        # Enable email enrichment (Fast mode = Apollo only, Thorough mode = waterfall)
        cmd.append("--enrich-emails")
        if self.config.get("waterfall_enrichment", False):
            cmd.append("--waterfall")
            await self._send_log("   Email enrichment: Thorough mode (Apollo -> Hunter -> Findymail)", "info")
        else:
            await self._send_log("   Email enrichment: Fast mode (Apollo only)", "info")

        # Skip LinkedIn and company research (email-only mode)
        cmd.append("--skip-linkedin")
        cmd.append("--skip-company-research")
        await self._send_log("   Skipping LinkedIn scraping and company research (email-only mode)", "info")

        # Add min_score filter
        min_score = self.config.get("min_score", 1)
        cmd.extend(["--min-score", str(min_score)])

        # Run subprocess with log streaming
        result = await self._run_subprocess_with_logs(cmd, str(phase2_dir))

        if result.returncode != 0:
            raise RuntimeError(f"Phase 2 (email-only) failed with return code {result.returncode}")

        # Find output path from file system
        output_dir = phase2_dir / "output"
        phase2_files = sorted(output_dir.glob("phase2_enriched_*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)

        if not phase2_files:
            raise RuntimeError("Phase 2 completed but no output CSV found")

        self.phase2_output = str(phase2_files[0].absolute())

        # Update metrics
        df_enriched = pd.read_csv(self.phase2_output)
        self.metrics["contacts_enriched"] = len(df_enriched)
        self.cost_tracker.add_phase2_email_cost(len(df_enriched))
        self.metrics["cost_actual"] = self.cost_tracker.get_total_cost()

        await self._update_metrics()
        await self._send_log(f"✓ Phase 2 (email-only) complete: {len(df_enriched)} contacts with verified emails", "success")
        await self._send_log("", "info")

    async def _run_phase3(self):
        """Run Phase 3: Message Generation as subprocess"""
        import json
        import tempfile

        self.current_stage = "phase3_messages"
        await self._send_log("✉️  PHASE 3: Message Generation", "info")

        phase3_dir = Path(__file__).parent.parent / "phase3_messages"

        # Prepare command
        cmd = [
            sys.executable,
            "run_phase3.py",
            self.phase2_output,
            self.config["message_mode"]
        ]

        # Add profile quality filter if specified
        if self.config.get("min_profile_quality") and self.config.get("min_profile_quality") > 1:
            cmd.extend(["--min-profile-quality", str(self.config["min_profile_quality"])])
            await self._send_log(f"Filtering for profile quality >= {self.config['min_profile_quality']}", "info")

        # Add company type override if specified
        if self.config.get("company_type_override"):
            cmd.extend(["--company-type", self.config["company_type_override"]])
            await self._send_log(f"Using industry override: {self.config['company_type_override']}", "info")

        # If custom template is provided, write it to temp file and pass path
        if self.config.get("custom_template"):
            temp_template_file = tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.json',
                delete=False,
                dir=str(phase3_dir)
            )
            json.dump(self.config["custom_template"], temp_template_file, indent=2)
            temp_template_file.close()

            # DEBUG LOGGING
            print(f"\n🔧 DEBUG Phase 3: Custom template written to: {temp_template_file.name}")
            print(f"   Template name: {self.config['custom_template'].get('name')}")
            print(f"   Passing to Phase 3 via --custom-template flag\n")

            cmd.extend(["--custom-template", temp_template_file.name])
            await self._send_log("Using custom template for this run", "info")

        # Add subject line config if provided (email mode only)
        subject_line_config = self.config.get("subject_line_config")
        if subject_line_config and self.config["message_mode"] == "email":
            cmd.extend(["--subject-line-style", subject_line_config.get("style", "question")])
            if subject_line_config.get("customPrompt"):
                cmd.extend(["--subject-line-prompt", subject_line_config["customPrompt"]])
            await self._send_log(f"Subject line generation: {subject_line_config.get('style', 'question')} style", "info")

        # Run subprocess with log streaming
        result = await self._run_subprocess_with_logs(cmd, str(phase3_dir))

        # Clean up temp template file if it exists
        if self.config.get("custom_template"):
            try:
                Path(temp_template_file.name).unlink()
            except:
                pass

        if result.returncode != 0:
            raise RuntimeError(f"Phase 3 failed with return code {result.returncode}")

        # Find output path from file system
        output_dir = phase3_dir / "output"
        pattern = f"phase3_messages_{self.config['message_mode']}_*.csv"
        phase3_files = sorted(output_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)

        if not phase3_files:
            raise RuntimeError("Phase 3 completed but no output CSV found")

        self.phase3_output = str(phase3_files[0].absolute())

        # Update metrics and costs
        df_messages = pd.read_csv(self.phase3_output)
        self.metrics["messages_generated"] = len(df_messages)
        self.cost_tracker.add_phase3_message_cost(len(df_messages))
        self.metrics["cost_actual"] = self.cost_tracker.get_total_cost()

        await self._update_metrics()
        await self._send_log(f"✓ Phase 3 complete: {len(df_messages)} message sequences generated", "success")

    async def _send_log(self, message: str, level: str = "info"):
        """Send log message via WebSocket"""
        await manager.send_log(self.job_id, message, level)

    async def _update_metrics(self):
        """Update and send current metrics"""
        # Calculate time
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            self.metrics["time_elapsed_seconds"] = elapsed

            # Estimate remaining time
            if self.metrics["messages_generated"] > 0:
                total_contacts = self.metrics["messages_generated_total"]
                progress = self.metrics["messages_generated"] / total_contacts if total_contacts > 0 else 0
                if progress > 0:
                    estimated_total_time = elapsed / progress
                    self.metrics["time_remaining_seconds"] = int(estimated_total_time - elapsed)

        # Update actual cost
        self.metrics["cost_actual"] = self.cost_tracker.get_total_cost()

        # Send metrics via WebSocket
        await manager.send_metrics(self.job_id, self.metrics)

    async def cancel(self):
        """Cancel the currently running pipeline"""
        if self.status in ["completed", "failed", "cancelled"]:
            return  # Already done, nothing to cancel

        self.cancelled = True
        self.status = "cancelled"
        self.error_message = "Pipeline cancelled by user"

        await self._send_log("🛑 Cancellation requested - stopping pipeline...", "warning")

        # If there's a running process, it will be terminated in _run_subprocess_with_logs
        # The subprocess runner checks self.cancelled in its loop

    async def pause(self):
        """Pause the currently running pipeline"""
        if self.status != "running":
            return  # Can only pause running pipelines

        self.status = "paused"
        await self._send_log("⏸️ Pipeline paused - checkpoint saved", "warning")

    async def resume(self):
        """Resume a paused pipeline"""
        if self.status != "paused":
            return  # Can only resume paused pipelines

        self.status = "running"
        await self._send_log("▶️ Pipeline resumed from checkpoint", "info")

    def get_status(self) -> Dict:
        """Get current pipeline status"""
        return {
            "job_id": self.job_id,
            "status": self.status,
            "current_stage": self.current_stage,
            "metrics": self.metrics,
            "error_message": self.error_message
        }
