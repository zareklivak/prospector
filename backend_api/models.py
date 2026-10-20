"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from datetime import datetime


class RoleLevels(BaseModel):
    """Role level checkboxes for Apollo seniority filtering"""
    c_suite: bool = Field(True, description="Include C-Suite and Head level (CEO, CTO, Head of X)")
    vp: bool = Field(True, description="Include VP level")
    director: bool = Field(True, description="Include Director level")
    manager: bool = Field(False, description="Include Manager level")


class SubjectLineConfig(BaseModel):
    """Configuration for AI-generated email subject lines"""
    style: Literal["question", "direct", "curiosity", "value", "custom"] = Field("question", description="Subject line style preset")
    customPrompt: Optional[str] = Field(None, description="Custom prompt for generating subject lines (used when style='custom')")


class PipelineConfig(BaseModel):
    """Configuration for running the full pipeline"""
    company_domains: List[str] = Field(..., description="List of company domains to scrape")
    contacts_per_company: int = Field(50, ge=1, le=500, description="Number of contacts per company")
    message_mode: Literal["email", "linkedin"] = Field("email", description="Message format mode")
    enrich_emails: bool = Field(True, description="Enrich & verify emails with Apollo + Instantly.ai verification")
    waterfall_enrichment: bool = Field(False, description="Use waterfall enrichment (Apollo -> Hunter -> Findymail). Default is Fast mode (Apollo only).")
    verify_current_employment: bool = Field(False, description="Whether to verify contacts are still at the target company using LinkedIn data (requires LinkedIn scrape)")
    skip_linkedin: bool = Field(False, description="Skip LinkedIn scraping in Phase 2 - generates messages from company research only (saves Apify credits)")
    min_score: int = Field(7, ge=1, le=10, description="Minimum ICP fit score for enrichment")
    min_profile_quality: int = Field(1, ge=1, le=10, description="Minimum profile quality score for message generation (1=all, 5=medium, 10=excellent)")
    custom_template: Optional[Dict] = Field(None, description="Custom template override for this run (per-run customization)")
    company_type_override: Optional[str] = Field(None, description="Optional industry/vertical selection to override auto-detection (affects use_cases_inline and value_prop_selection variables)")
    prospect_only: bool = Field(False, description="If true, only run Phase 1 (prospecting) and skip enrichment & message generation")
    role_levels: Optional[RoleLevels] = Field(None, description="Role level filters for Apollo seniority (defaults to Director+)")
    max_initial_scrape: int = Field(2000, ge=100, le=10000, description="Maximum contacts to scrape from Apollo before scoring/filtering")
    include_unverified_contacts: bool = Field(False, description="Include contacts without verified/guessed emails (useful for LinkedIn-only outreach)")
    subject_line_config: Optional[SubjectLineConfig] = Field(None, description="Configuration for AI-generated email subject lines (email mode only)")


class TestTemplateRequest(BaseModel):
    """Request to test message templates on sample prospects"""
    message_mode: Literal["email", "linkedin", "linkedin_dm"] = Field("email", description="Message format mode (linkedin_dm is treated as linkedin)")
    custom_template: Optional[Dict] = Field(None, description="Custom template to test (full unified template)")
    company_type_override: Optional[str] = Field(None, description="Optional industry override for testing specific use cases (e.g., 'broker', 'air freight')")


class PipelineResponse(BaseModel):
    """Response when starting a pipeline"""
    job_id: str = Field(..., description="Unique job identifier")
    status: Literal["queued", "running", "complete", "error"] = Field(..., description="Job status")
    websocket_url: str = Field(..., description="WebSocket URL for live updates")


class JobStatus(BaseModel):
    """Current status of a pipeline job"""
    job_id: str
    status: Literal["queued", "running", "complete", "error"]
    current_stage: Optional[str] = None
    percent_complete: int = 0
    error_message: Optional[str] = None


class MetricsUpdate(BaseModel):
    """Real-time metrics update"""
    stage: str
    companies_total: int
    companies_done: int
    contacts_scraped: int
    contacts_scraped_total: int
    contacts_enriched: int
    contacts_enriched_total: int
    messages_generated: int
    messages_generated_total: int
    cost_estimated: float
    cost_actual: float
    time_elapsed_seconds: int
    time_remaining_seconds: int


class LogEntry(BaseModel):
    """Single log entry"""
    timestamp: str
    level: Literal["info", "success", "warning", "error"]
    message: str


class WebSocketMessage(BaseModel):
    """Message sent over WebSocket"""
    type: Literal["log", "metrics", "complete", "error"]
    data: Dict


class SampleProspect(BaseModel):
    """Hardcoded sample prospect for testing"""
    first_name: str
    last_name: str
    title: str
    company_name: str
    company_domain: str
    personal_research: str
    company_research: str


class TestTemplateResponse(BaseModel):
    """Response from testing templates on sample prospects"""
    prospects: List[Dict]  # List of prospects with generated messages
    generation_time: float
    model_used: str
