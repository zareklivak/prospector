# Prospector - Backend API

FastAPI backend wrapper for the 3-phase prospecting pipeline.

## Setup

1. **Install dependencies:**
```bash
cd backend_api
pip install -r requirements.txt
```

2. **Ensure .env file exists in project root with API keys:**
```bash
# Required API keys
APOLLO_API_KEY=your_key
APIFY_API_TOKEN=your_token
PERPLEXITY_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
```

## Running the Server

**Development mode (with auto-reload):**
```bash
cd backend_api
python main.py
```

**Or using uvicorn directly:**
```bash
cd backend_api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: `http://localhost:8000`

## API Endpoints

### 1. Health Check
```bash
GET /
```

### 2. Run Pipeline
```bash
POST /api/run-pipeline
Content-Type: application/json

{
  "company_domains": ["fedex.com", "ups.com"],
  "contacts_per_company": 50,
  "message_mode": "email",
  "enrich_emails": true,
  "min_score": 7,
  "system_prompt": null
}
```

**Response:**
```json
{
  "job_id": "a3b4c5d6",
  "status": "running",
  "websocket_url": "/ws/a3b4c5d6"
}
```

### 3. Get Job Status
```bash
GET /api/job-status/{job_id}
```

**Response:**
```json
{
  "job_id": "a3b4c5d6",
  "status": "running",
  "current_stage": "phase2_enrichment",
  "percent_complete": 42,
  "error_message": null
}
```

### 4. Download CSV
```bash
GET /api/download-csv/{job_id}
```

Returns CSV file download.

### 5. Test Templates
```bash
POST /api/test-templates
Content-Type: application/json

{
  "system_prompt": "Your custom system prompt here...",
  "message_mode": "email"
}
```

**Response:**
```json
{
  "prospects": [
    {
      "prospect": {...},
      "messages": {
        "message_1": "...",
        "message_2": "...",
        "message_3": "...",
        "message_4": "..."
      }
    }
  ],
  "generation_time": 12.5,
  "model_used": "claude-sonnet-4-5"
}
```

### 6. Get Sample Prospects
```bash
GET /api/sample-prospects
```

Returns 3 hardcoded sample prospects for testing.

### 7. WebSocket Connection
```
WS /ws/{job_id}
```

Connects to live pipeline updates. Receives messages:

**Log messages:**
```json
{
  "type": "log",
  "timestamp": "2025-10-30T10:23:15",
  "level": "info",
  "message": "Phase 1: Scraped 52 contacts @ fedex.com"
}
```

**Metrics updates:**
```json
{
  "type": "metrics",
  "data": {
    "stage": "phase2_enrichment",
    "companies_total": 3,
    "companies_done": 2,
    "contacts_scraped": 147,
    "contacts_enriched": 89,
    "messages_generated": 0,
    "cost_estimated": 7.50,
    "cost_actual": 4.23,
    "time_elapsed_seconds": 312,
    "time_remaining_seconds": 145
  }
}
```

**Completion message:**
```json
{
  "type": "complete",
  "csv_path": "/path/to/output.csv",
  "timestamp": "2025-10-30T10:35:42"
}
```

## Testing with curl

**1. Start a pipeline:**
```bash
curl -X POST http://localhost:8000/api/run-pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "company_domains": ["fedex.com"],
    "contacts_per_company": 10,
    "message_mode": "email",
    "enrich_emails": false,
    "min_score": 7
  }'
```

**2. Check job status:**
```bash
curl http://localhost:8000/api/job-status/a3b4c5d6
```

**3. Test templates:**
```bash
curl -X POST http://localhost:8000/api/test-templates \
  -H "Content-Type: application/json" \
  -d '{
    "system_prompt": "Generate friendly outreach messages...",
    "message_mode": "email"
  }'
```

## Architecture

```
Frontend (Lovable)
    ↓ POST /api/run-pipeline
    ↓ WS /ws/{job_id}
Backend API (FastAPI)
    ↓
PipelineOrchestrator
    ↓
Phase 1 → Phase 2 → Phase 3
```

## Development Notes

- **In-memory job storage:** Jobs are lost on server restart (simple MVP approach)
- **Log capture:** Uses stdout redirection to capture Phase 1/2/3 print statements
- **WebSocket:** Provides real-time updates to frontend
- **CORS:** Configured to allow all origins (update for production)

## Next Steps

1. Test all endpoints with curl/Postman
2. Build Lovable frontend
3. Connect frontend to backend
4. Deploy to production (Docker + hosting)
