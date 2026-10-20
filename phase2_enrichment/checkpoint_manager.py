"""
Checkpoint Manager for Phase 2 Enrichment

Saves progress incrementally to prevent data loss during long runs.
Supports resume from any step in the 5-step enrichment flow.
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any
import hashlib


class CheckpointManager:
    """
    Manages checkpoint files for Phase 2 enrichment pipeline.

    Checkpoint structure:
    {
        "job_id": unique identifier based on input file + parameters,
        "input_file": path to input CSV,
        "created_at": timestamp,
        "updated_at": timestamp,
        "config": {enrich_emails, verify_emails, min_score, min_profile_quality},
        "current_step": 1-5 (which step we're on),
        "step_status": {
            "email_enrichment": "complete|in_progress|pending",
            "email_verification": "complete|in_progress|pending|skipped",
            "linkedin_scraping": "complete|in_progress|pending",
            "profile_quality_filter": "complete|in_progress|pending|skipped",
            "company_research": "complete|in_progress|pending"
        },
        "processed_indices": list of row indices that have been processed,
        "data_file": path to checkpoint CSV with partial results
    }
    """

    CHECKPOINT_DIR = os.path.join(os.path.dirname(__file__), "checkpoints")

    def __init__(self):
        os.makedirs(self.CHECKPOINT_DIR, exist_ok=True)

    def _generate_job_id(self, input_csv: str, config: Dict) -> str:
        """Generate a unique job ID based on input file and config"""
        # Use input filename + key config parameters to create unique ID
        # Include all config params that affect pipeline behavior
        config_str = f"{input_csv}_{config.get('enrich_emails')}_{config.get('verify_emails')}_{config.get('verify_current_employment')}_{config.get('min_score')}_{config.get('min_profile_quality')}"
        hash_id = hashlib.md5(config_str.encode()).hexdigest()[:12]
        return f"phase2_{hash_id}"

    def _get_checkpoint_path(self, job_id: str) -> str:
        """Get path to checkpoint JSON file"""
        return os.path.join(self.CHECKPOINT_DIR, f"{job_id}_checkpoint.json")

    def _get_data_path(self, job_id: str) -> str:
        """Get path to checkpoint data CSV file"""
        return os.path.join(self.CHECKPOINT_DIR, f"{job_id}_data.csv")

    def find_checkpoint(self, input_csv: str, config: Dict) -> Optional[Dict]:
        """
        Check if a checkpoint exists for this job.
        Returns checkpoint data if found, None otherwise.
        """
        job_id = self._generate_job_id(input_csv, config)
        checkpoint_path = self._get_checkpoint_path(job_id)

        if os.path.exists(checkpoint_path):
            try:
                with open(checkpoint_path, 'r') as f:
                    checkpoint = json.load(f)

                # Verify data file exists
                if os.path.exists(checkpoint.get("data_file", "")):
                    return checkpoint
                else:
                    print(f"   [Checkpoint] Data file missing, ignoring checkpoint")
                    return None
            except Exception as e:
                print(f"   [Checkpoint] Error loading checkpoint: {e}")
                return None

        return None

    def create_checkpoint(
        self,
        input_csv: str,
        config: Dict,
        df: pd.DataFrame,
        current_step: int = 1,
        step_status: Optional[Dict] = None
    ) -> str:
        """
        Create a new checkpoint or update existing one.

        Args:
            input_csv: Original input file path
            config: Pipeline configuration
            df: Current DataFrame with partial results
            current_step: Current step number (1-5)
            step_status: Status of each step

        Returns:
            job_id for this checkpoint
        """
        job_id = self._generate_job_id(input_csv, config)
        checkpoint_path = self._get_checkpoint_path(job_id)
        data_path = self._get_data_path(job_id)

        # Default step status
        if step_status is None:
            step_status = {
                "email_enrichment": "pending",
                "email_verification": "pending",
                "linkedin_scraping": "pending",
                "profile_quality_filter": "pending",
                "company_research": "pending"
            }

        # Save data to CSV
        df.to_csv(data_path, index=False)

        # Create checkpoint metadata
        checkpoint = {
            "job_id": job_id,
            "input_file": input_csv,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "config": config,
            "current_step": current_step,
            "step_status": step_status,
            "total_contacts": len(df),
            "data_file": data_path
        }

        # Save checkpoint
        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint, f, indent=2)

        return job_id

    def update_checkpoint(
        self,
        job_id: str,
        df: pd.DataFrame,
        current_step: Optional[int] = None,
        step_status: Optional[Dict] = None
    ) -> None:
        """Update an existing checkpoint with new progress"""
        checkpoint_path = self._get_checkpoint_path(job_id)
        data_path = self._get_data_path(job_id)

        if not os.path.exists(checkpoint_path):
            raise ValueError(f"Checkpoint not found: {job_id}")

        # Load existing checkpoint
        with open(checkpoint_path, 'r') as f:
            checkpoint = json.load(f)

        # Save updated data
        df.to_csv(data_path, index=False)

        # Update metadata
        checkpoint["updated_at"] = datetime.now().isoformat()
        checkpoint["total_contacts"] = len(df)

        if current_step is not None:
            checkpoint["current_step"] = current_step

        if step_status is not None:
            checkpoint["step_status"] = step_status

        # Save updated checkpoint
        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint, f, indent=2)

    def load_checkpoint_data(self, checkpoint: Dict) -> pd.DataFrame:
        """Load the DataFrame from a checkpoint"""
        data_path = checkpoint.get("data_file", "")
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Checkpoint data file not found: {data_path}")

        return pd.read_csv(data_path)

    def delete_checkpoint(self, job_id: str) -> None:
        """Delete a checkpoint and its data file"""
        checkpoint_path = self._get_checkpoint_path(job_id)
        data_path = self._get_data_path(job_id)

        if os.path.exists(checkpoint_path):
            os.remove(checkpoint_path)

        if os.path.exists(data_path):
            os.remove(data_path)

    def list_checkpoints(self) -> list:
        """List all available checkpoints"""
        checkpoints = []
        for filename in os.listdir(self.CHECKPOINT_DIR):
            if filename.endswith("_checkpoint.json"):
                checkpoint_path = os.path.join(self.CHECKPOINT_DIR, filename)
                try:
                    with open(checkpoint_path, 'r') as f:
                        checkpoint = json.load(f)
                    checkpoints.append({
                        "job_id": checkpoint["job_id"],
                        "input_file": checkpoint["input_file"],
                        "created_at": checkpoint["created_at"],
                        "updated_at": checkpoint["updated_at"],
                        "current_step": checkpoint["current_step"],
                        "total_contacts": checkpoint.get("total_contacts", 0)
                    })
                except Exception:
                    pass

        return checkpoints

    def get_step_name(self, step_num: int) -> str:
        """Get human-readable name for step number"""
        steps = {
            1: "Email Enrichment (Apollo)",
            2: "Email Verification (Instantly.ai)",
            3: "LinkedIn Scraping (Apify)",
            4: "Profile Quality Filter",
            5: "Company Research (Perplexity)"
        }
        return steps.get(step_num, f"Step {step_num}")
