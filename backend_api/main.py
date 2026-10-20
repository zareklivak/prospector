"""
FastAPI Backend for Prospector
"""
import asyncio
import uuid
from pathlib import Path
from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from backend_api.models import (
    PipelineConfig,
    PipelineResponse,
    JobStatus,
    TestTemplateRequest,
    TestTemplateResponse
)
from backend_api.pipeline import PipelineOrchestrator
from backend_api.websocket_handler import manager
from backend_api.config import SAMPLE_PROSPECTS, OUTPUT_DIR

# Initialize FastAPI app
app = FastAPI(
    title="Prospector API",
    description="Backend API for automated B2B prospecting pipeline",
    version="1.0.0"
)

# CORS configuration (allow Lovable frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific Lovable domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job storage
jobs: Dict[str, PipelineOrchestrator] = {}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Prospector API is running",
        "version": "1.0.0"
    }


@app.get("/api/status")
async def api_status():
    """Check API key status for all services"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Check which API keys are configured
    apis = {
        "apollo": {
            "name": "Apollo.io",
            "description": "Contact scraping & email enrichment",
            "connected": bool(os.getenv("APOLLO_API_KEY")),
            "required": True
        },
        "apify": {
            "name": "Apify",
            "description": "LinkedIn posts & profile scraping",
            "connected": bool(os.getenv("APIFY_API_TOKEN")),
            "required": True
        },
        "perplexity": {
            "name": "Perplexity",
            "description": "Company research",
            "connected": bool(os.getenv("PERPLEXITY_API_KEY")),
            "required": True
        },
        "anthropic": {
            "name": "Anthropic",
            "description": "Message generation (Claude)",
            "connected": bool(os.getenv("ANTHROPIC_API_KEY")),
            "required": True
        },
        "openai": {
            "name": "OpenAI",
            "description": "Message generation (GPT-4)",
            "connected": bool(os.getenv("OPENAI_API_KEY")),
            "required": True
        },
        "instantly": {
            "name": "Instantly.ai",
            "description": "Email verification",
            "connected": bool(os.getenv("INSTANTLY_API_KEY")),
            "required": False
        }
    }

    return {"apis": apis}


@app.post("/api/run-pipeline", response_model=PipelineResponse)
async def run_pipeline(config: PipelineConfig):
    """
    Start a new pipeline run

    Args:
        config: Pipeline configuration

    Returns:
        Job ID and WebSocket URL for tracking progress
    """
    # Generate unique job ID
    job_id = str(uuid.uuid4())[:8]

    # DEBUG LOGGING
    print(f"\n{'='*80}")
    print(f"🔧 DEBUG: Received pipeline request")
    print(f"📋 Companies: {config.company_domains}")
    print(f"📊 Contacts per company: {config.contacts_per_company}")
    print(f"✉️  Mode: {config.message_mode}")
    print(f"📧 Enrich & verify emails: {config.enrich_emails}")
    if config.enrich_emails:
        print(f"   Mode: {'Thorough (waterfall)' if config.waterfall_enrichment else 'Fast (Apollo only)'}")
    print(f"👔 Verify current employment: {config.verify_current_employment}")
    print(f"⏭️  Skip LinkedIn scraping: {config.skip_linkedin}")
    print(f"🎯 Min ICP score: {config.min_score}")
    print(f"⭐ Min profile quality: {config.min_profile_quality}")
    print(f"🏭 Company type override: {config.company_type_override or 'Auto-detect'}")
    print(f"📇 Prospect-only mode: {config.prospect_only}")
    print(f"👔 Role levels: {config.role_levels}")
    print(f"📥 Max initial scrape: {config.max_initial_scrape}")
    print(f"🎨 Custom template received: {config.custom_template is not None}")
    if config.custom_template:
        print(f"   Template name: {config.custom_template.get('name', 'Unknown')}")
        print(f"   Template mode: {config.custom_template.get('mode', 'Unknown')}")
    print(f"📝 Subject line config: {config.subject_line_config}")
    print(f"{'='*80}\n")

    # Create pipeline orchestrator
    pipeline_config = {
        "company_domains": config.company_domains,
        "contacts_per_company": config.contacts_per_company,
        "message_mode": config.message_mode,
        "enrich_emails": config.enrich_emails,
        "waterfall_enrichment": config.waterfall_enrichment,
        "verify_current_employment": config.verify_current_employment,
        "skip_linkedin": config.skip_linkedin,
        "min_score": config.min_score,
        "min_profile_quality": config.min_profile_quality,
        "custom_template": config.custom_template,
        "company_type_override": config.company_type_override,
        "prospect_only": config.prospect_only,
        "role_levels": config.role_levels.model_dump() if config.role_levels else None,
        "max_initial_scrape": config.max_initial_scrape,
        "include_unverified_contacts": config.include_unverified_contacts,
        "subject_line_config": config.subject_line_config.model_dump() if config.subject_line_config else None
    }

    orchestrator = PipelineOrchestrator(job_id, pipeline_config)
    jobs[job_id] = orchestrator

    # Run pipeline in background
    asyncio.create_task(orchestrator.run())

    return PipelineResponse(
        job_id=job_id,
        status="running",
        websocket_url=f"/ws/{job_id}"
    )


@app.get("/api/job-status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """
    Get current status of a pipeline job

    Args:
        job_id: Job identifier

    Returns:
        Current job status and progress
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    orchestrator = jobs[job_id]
    status_data = orchestrator.get_status()

    return JobStatus(
        job_id=status_data["job_id"],
        status=status_data["status"],
        current_stage=status_data["current_stage"],
        percent_complete=int(
            (status_data["metrics"]["messages_generated"] /
             max(status_data["metrics"]["messages_generated_total"], 1)) * 100
        ),
        error_message=status_data["error_message"]
    )


@app.post("/api/cancel-pipeline/{job_id}")
async def cancel_pipeline(job_id: str):
    """
    Cancel a running pipeline

    Args:
        job_id: Job identifier

    Returns:
        Success message
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    orchestrator = jobs[job_id]

    # Can only cancel running pipelines
    if orchestrator.status not in ["running", "queued"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel pipeline with status: {orchestrator.status}"
        )

    # Cancel the pipeline
    await orchestrator.cancel()

    return {"message": "Pipeline cancellation initiated", "job_id": job_id}


@app.post("/api/pause-pipeline/{job_id}")
async def pause_pipeline(job_id: str):
    """
    Pause a running pipeline (saves checkpoint and waits)

    Args:
        job_id: Job identifier

    Returns:
        Success message
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    orchestrator = jobs[job_id]

    # Can only pause running pipelines
    if orchestrator.status != "running":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot pause pipeline with status: {orchestrator.status}"
        )

    # Pause the pipeline
    await orchestrator.pause()

    return {
        "message": "Pipeline paused - checkpoint saved",
        "job_id": job_id,
        "status": "paused"
    }


@app.post("/api/resume-pipeline/{job_id}")
async def resume_pipeline(job_id: str):
    """
    Resume a paused pipeline from checkpoint

    Args:
        job_id: Job identifier

    Returns:
        Success message
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    orchestrator = jobs[job_id]

    # Can only resume paused pipelines
    if orchestrator.status != "paused":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot resume pipeline with status: {orchestrator.status}"
        )

    # Resume the pipeline
    await orchestrator.resume()

    return {
        "message": "Pipeline resumed from checkpoint",
        "job_id": job_id,
        "status": "running"
    }


@app.get("/api/checkpoints")
async def list_checkpoints():
    """
    List all available checkpoints for resuming

    Returns:
        List of checkpoint metadata
    """
    import sys
    from pathlib import Path

    # Add phase2 to path
    sys.path.insert(0, str(Path(__file__).parent.parent / "phase2_enrichment"))

    from checkpoint_manager import CheckpointManager

    checkpoint_mgr = CheckpointManager()
    checkpoints = checkpoint_mgr.list_checkpoints()

    return {"checkpoints": checkpoints}


@app.get("/api/download-csv/{job_id}")
async def download_csv(job_id: str):
    """
    Download the final CSV output for a completed job
    Returns Phase 1 CSV for prospect-only mode, Phase 3 CSV for full pipeline

    Args:
        job_id: Job identifier

    Returns:
        CSV file download
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    orchestrator = jobs[job_id]

    if orchestrator.status != "complete":
        raise HTTPException(status_code=400, detail="Job is not complete yet")

    # Determine which output file to return based on mode
    prospect_only = orchestrator.config.get("prospect_only", False)
    enrich_emails = orchestrator.config.get("enrich_emails", False)

    if prospect_only:
        if enrich_emails:
            # Prospect-only + email enrichment: return Phase 2 output (has verified emails + email_source)
            output_path = orchestrator.phase2_output
            output_type = "prospects_enriched"
        else:
            # Standard prospect-only mode (no enrichment): return Phase 1 output
            output_path = orchestrator.phase1_output
            output_type = "prospects"
    else:
        # Full pipeline mode: return Phase 3 output
        output_path = orchestrator.phase3_output
        output_type = "messages"

    if not output_path or not Path(output_path).exists():
        raise HTTPException(status_code=404, detail="Output file not found")

    return FileResponse(
        path=output_path,
        filename=f"prospector_{output_type}_{job_id}.csv",
        media_type="text/csv"
    )


@app.post("/api/test-templates", response_model=TestTemplateResponse)
async def test_templates(request: TestTemplateRequest):
    """
    Test message templates on hardcoded sample prospects

    Args:
        request: Message mode and optional custom template

    Returns:
        Generated messages for 3 sample prospects
    """
    import sys
    import time
    import json
    import tempfile
    from pathlib import Path

    # Add phase3 to path
    sys.path.insert(0, str(Path(__file__).parent.parent / "phase3_messages"))

    from phase3_messages.batch_message_generator import BatchMessageGenerator
    import phase3_messages.config as phase3_config

    # DEBUG LOGGING
    print(f"\n{'='*80}")
    print(f"🔧 DEBUG: Test templates request")
    print(f"✉️  Mode: {request.message_mode}")
    print(f"🎨 Custom template received: {request.custom_template is not None}")
    print(f"🎯 Industry override: {request.company_type_override or 'auto-detect'}")
    if request.custom_template:
        print(f"   Template name: {request.custom_template.get('name', 'Unknown')}")
        print(f"   Template mode: {request.custom_template.get('mode', 'Unknown')}")
    print(f"{'='*80}\n")

    try:
        # If custom template provided, write to temp file
        custom_template_path = None
        temp_template_file = None

        if request.custom_template:
            phase3_dir = Path(__file__).parent.parent / "phase3_messages"
            temp_template_file = tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.json',
                delete=False,
                dir=str(phase3_dir)
            )
            json.dump(request.custom_template, temp_template_file, indent=2)
            temp_template_file.close()
            custom_template_path = temp_template_file.name

            print(f"🔧 DEBUG: Custom template written to: {custom_template_path}\n")

        # Initialize message generator with custom template if provided
        generator = BatchMessageGenerator(
            llm_provider="claude",
            custom_template_path=custom_template_path
        )

        # Get prospects based on industry filter (uses company_type_override)
        from backend_api.config import get_prospects_for_testing
        prospects = get_prospects_for_testing(request.company_type_override)

        print(f"📊 Testing with {len(prospects)} prospects")
        if request.company_type_override and request.company_type_override != "auto-detect":
            print(f"   Filtered to industry: {request.company_type_override}")
        else:
            print(f"   Using default diverse set (broker, carrier, 3PL)")
        print()

        results = []
        start_time = time.time()

        # Normalize message mode (linkedin_dm -> linkedin)
        effective_mode = "linkedin" if request.message_mode == "linkedin_dm" else request.message_mode

        # Generate messages for each sample prospect
        for prospect in prospects:
            # Convert dict to pandas Series
            import pandas as pd
            contact_series = pd.Series(prospect)

            messages = generator.generate_batch_sequence(
                contact_row=contact_series,
                mode=effective_mode,
                company_type_override=request.company_type_override
            )

            results.append({
                "prospect": prospect,
                "messages": messages
            })

        generation_time = time.time() - start_time

        # Clean up temp template file
        if temp_template_file:
            try:
                Path(temp_template_file.name).unlink()
            except:
                pass

        return TestTemplateResponse(
            prospects=results,
            generation_time=round(generation_time, 2),
            model_used="claude-sonnet-4-5"
        )

    except Exception as e:
        # Clean up temp file on error
        if temp_template_file:
            try:
                Path(temp_template_file.name).unlink()
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Template testing failed: {str(e)}")


@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time pipeline updates

    Args:
        websocket: WebSocket connection
        job_id: Job identifier
    """
    if job_id not in jobs:
        await websocket.close(code=1008, reason="Job not found")
        return

    await manager.connect(websocket, job_id)

    try:
        # Keep connection alive and listen for client messages
        while True:
            # Wait for client ping/pong
            data = await websocket.receive_text()

            # Optionally handle client messages here
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)
    except Exception as e:
        print(f"[WebSocket] Error: {e}")
        manager.disconnect(websocket, job_id)


@app.get("/api/sample-prospects")
async def get_sample_prospects():
    """
    Get the hardcoded sample prospects for testing

    Returns:
        List of 3 sample prospects
    """
    return {"prospects": SAMPLE_PROSPECTS}


@app.get("/api/unified-templates/{mode}")
async def get_unified_template(mode: str):
    """
    Get default template for a mode (email or linkedin)

    Args:
        mode: "email" or "linkedin"

    Returns:
        Default template JSON with all message structures, system prompt, style guide, etc.
    """
    import json
    from pathlib import Path

    if mode not in ["email", "linkedin"]:
        raise HTTPException(status_code=400, detail="Mode must be 'email' or 'linkedin'")

    template_path = Path(__file__).parent.parent / "phase3_messages" / "templates" / f"default_{mode}_template.json"

    if not template_path.exists():
        raise HTTPException(status_code=404, detail=f"Template file not found: {template_path}")

    with open(template_path, 'r') as f:
        template = json.load(f)

    return template


@app.put("/api/unified-templates/{mode}")
async def update_unified_template(mode: str, template: dict):
    """
    Save updated unified template

    Args:
        mode: "email" or "linkedin"
        template: Updated template JSON

    Returns:
        Success message
    """
    import json
    from pathlib import Path

    if mode not in ["email", "linkedin"]:
        raise HTTPException(status_code=400, detail="Mode must be 'email' or 'linkedin'")

    template_path = Path(__file__).parent.parent / "phase3_messages" / "templates" / f"unified_{mode}_template.json"

    try:
        with open(template_path, 'w') as f:
            json.dump(template, f, indent=2)

        return {"message": f"Template updated successfully", "mode": mode}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save template: {str(e)}")


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a job and clean up resources

    Args:
        job_id: Job identifier

    Returns:
        Success message
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    del jobs[job_id]

    return {"message": f"Job {job_id} deleted successfully"}


@app.get("/api/saved-templates")
async def list_saved_templates():
    """
    List all saved custom templates

    Returns:
        List of template metadata (name, mode, created_at)
    """
    import json
    from datetime import datetime

    templates_dir = Path(__file__).parent.parent / "phase3_messages" / "templates" / "saved"
    templates_dir.mkdir(parents=True, exist_ok=True)

    templates = []
    for template_file in templates_dir.glob("*.json"):
        try:
            with open(template_file, 'r') as f:
                data = json.load(f)
                templates.append({
                    "id": template_file.stem,  # filename without extension
                    "name": data.get("name", template_file.stem),
                    "mode": data.get("mode", "email"),
                    "created_at": datetime.fromtimestamp(template_file.stat().st_mtime).isoformat()
                })
        except Exception as e:
            print(f"Warning: Could not load template {template_file}: {e}")
            continue

    # Sort by created_at descending (newest first)
    templates.sort(key=lambda x: x["created_at"], reverse=True)

    return {"templates": templates}


@app.post("/api/saved-templates")
async def save_custom_template(request: dict):
    """
    Save a custom template with a user-provided name

    Args:
        request: {
            "name": "My Custom Template",
            "template": {template object}
        }

    Returns:
        Success message with template ID
    """
    import json
    import re

    name = request.get("name")
    template = request.get("template")

    if not name:
        raise HTTPException(status_code=400, detail="Template name is required")
    if not template:
        raise HTTPException(status_code=400, detail="Template data is required")

    # Sanitize name for filename (remove special chars, replace spaces with underscores)
    safe_name = re.sub(r'[^a-zA-Z0-9\s_-]', '', name)  # Keep underscores too
    safe_name = re.sub(r'\s+', '_', safe_name).lower()

    if not safe_name:
        raise HTTPException(status_code=400, detail="Invalid template name")

    templates_dir = Path(__file__).parent.parent / "phase3_messages" / "templates" / "saved"
    templates_dir.mkdir(parents=True, exist_ok=True)

    template_path = templates_dir / f"{safe_name}.json"

    # Update template name field to match user input
    template["name"] = name

    try:
        with open(template_path, 'w') as f:
            json.dump(template, f, indent=2)

        return {
            "message": "Template saved successfully",
            "id": safe_name,
            "name": name,
            "path": str(template_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save template: {str(e)}")


@app.get("/api/saved-templates/{template_id}")
async def get_saved_template(template_id: str):
    """
    Load a saved custom template by ID

    Args:
        template_id: Template identifier (filename without extension)

    Returns:
        Template JSON object
    """
    import json

    templates_dir = Path(__file__).parent.parent / "phase3_messages" / "templates" / "saved"
    template_path = templates_dir / f"{template_id}.json"

    if not template_path.exists():
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")

    try:
        with open(template_path, 'r') as f:
            template = json.load(f)
        return template
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load template: {str(e)}")


@app.delete("/api/saved-templates/{template_id}")
async def delete_saved_template(template_id: str):
    """
    Delete a saved custom template

    Args:
        template_id: Template identifier (filename without extension)

    Returns:
        Success message
    """
    templates_dir = Path(__file__).parent.parent / "phase3_messages" / "templates" / "saved"
    template_path = templates_dir / f"{template_id}.json"

    if not template_path.exists():
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")

    try:
        template_path.unlink()
        return {"message": f"Template '{template_id}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete template: {str(e)}")


@app.put("/api/saved-templates/{template_id}")
async def update_saved_template(template_id: str, request: dict):
    """
    Update an existing saved template in place

    Args:
        template_id: Template identifier (filename without extension)
        request: {
            "template": {template object}
        }

    Returns:
        Success message with template details
    """
    import json

    template = request.get("template")

    if not template:
        raise HTTPException(status_code=400, detail="Template data is required")

    templates_dir = Path(__file__).parent.parent / "phase3_messages" / "templates" / "saved"
    template_path = templates_dir / f"{template_id}.json"

    if not template_path.exists():
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")

    try:
        # Preserve the template name from the existing file or use from request
        with open(template_path, 'r') as f:
            existing = json.load(f)

        # Keep the original name if not provided
        if "name" not in template:
            template["name"] = existing.get("name", template_id)

        with open(template_path, 'w') as f:
            json.dump(template, f, indent=2)

        return {
            "message": "Template updated successfully",
            "id": template_id,
            "name": template.get("name", template_id),
            "path": str(template_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update template: {str(e)}")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("🚀 Prospector API starting...")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print("✅ Ready to accept requests")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 Prospector API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
