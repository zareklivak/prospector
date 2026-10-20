# Prospector

**Company domains in, ready-to-send personalized sequences out.** A three-phase AI prospecting pipeline with a web UI: it finds the right people at target accounts, enriches and verifies them, researches each company once, and writes a 4-step email or LinkedIn sequence per contact grounded in that research, with live logs and per-run cost tracking.

> **Scenario:** built to prospect for *Waypoint*, a stand-in for an AI voice-agent company selling into logistics (freight brokers, carriers, shippers). The vertical lives in config (`phase3_messages/use_case_config.py`, the templates), not in the pipeline.

---

## How it works

```
 domains ─▶ PHASE 1: find + score ─▶ PHASE 2: enrich + verify ─▶ PHASE 3: write ─▶ CSV
            Apollo search             LinkedIn profile + posts        vertical detection
            Director+ only            (Apify)                         use-case match by title
            role-fit scoring          still-employed check            1 LLM call = 4 messages
            top N per company         company research, cached        Claude or OpenAI
                                      (Perplexity)                    editable JSON templates
                                      email waterfall + verify
```

**Phase 1 - Find and score** (`phase1_apollo/`): pulls Director / VP / Head / C-suite contacts from Apollo, scores each on role fit with a configurable keyword model (`config/scoring_config.json`), and keeps the top N per company. Credits are only spent on contacts that will survive scoring.

**Phase 2 - Enrich and verify** (`phase2_enrichment/`):
- LinkedIn profile and recent posts via Apify actors, so messages can reference what the person actually said.
- **Employment verification:** fuzzy-matches the Apollo company against the person's *current* LinkedIn position, dropping contacts who already left (the most common cause of embarrassing cold email).
- **Company research once, reused for every contact** at that company (Perplexity), which keeps cost flat as contacts per account grow.
- **Email waterfall:** Fast mode (Apollo only, about 97% coverage) or Thorough mode (Apollo → Hunter → Findymail). Every email must match the company domain and pass Instantly verification before it's kept.
- **Checkpointed:** long runs save progress per step and resume where they stopped.

**Phase 3 - Write** (`phase3_messages/`): detects the company's vertical from the research, picks the 2-3 use cases most relevant to *this person's title* (a recruiting lead hears about driver recruiting, a sales leader about inbound quoting), and generates all four sequence steps in a single LLM call. Templates, tone rules, banned phrases and signatures are JSON, editable from the UI.

**App** (`backend_api/` + `frontend/`): FastAPI backend with a WebSocket stream of live pipeline logs, real-time cost tracking per phase, and a React UI for configuring runs, editing templates, and downloading each phase's CSV.

## Design choices

- **Spend credits last.** Score before enriching, verify before keeping, research per company rather than per person. Cost per finished contact is shown live, not discovered on the invoice.
- **A wrong person is worse than no person.** Domain matching, the employment check, and independent verification exist to protect sender reputation.
- **Relevance from structure, not vibes.** Use cases are chosen by a vertical × title mapping first; the LLM writes from that selection and the research, under explicit style rules (no buzzwords, one idea per message).

## Run it

```bash
# backend
pip install -r backend_api/requirements.txt
cp .env.example .env                    # fill in the API keys
python start_server.py                  # http://localhost:8000

# frontend
cd frontend && npm install && npm run dev
```

Each phase also runs standalone (`python phase1_apollo/run_phase1.py`, etc.); see the README in each phase folder.

## Stack

Python · FastAPI + WebSockets · React + TypeScript + Tailwind (Vite) · Apollo · Apify · Perplexity · Hunter · Findymail · Instantly · Claude / OpenAI
