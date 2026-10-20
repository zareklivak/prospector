# Phase 2: Contact Enrichment

Enriches Phase 1 contacts with personalization data from LinkedIn, Apollo, and company research for Waypoint sales.

## What Phase 2 Does

1. **Apollo Email Enrichment** (optional) - Get real emails by spending Apollo credits
2. **LinkedIn Post Scraping** (Apify) - Recent 5 posts for personalization
3. **LinkedIn Profile Scraping** (Apify) - Headline, experience, about section
4. **Company Research** (Perplexity) - One research per company, cached and reused

## Cost Controls

- **Apify**: ~$0.05 per contact (2 actor calls)
- **Perplexity**: ~$0.001 per company (cached)
- **Apollo**: ~$0.10 per contact (optional, only if `--enrich-emails` flag used)

## Usage

### Basic Usage (No email enrichment)
```bash
python main.py ../phase1_apollo/output/phase1_ranked_contacts.csv
```

### With Email Enrichment (Spends Apollo Credits!)
```bash
python main.py ../phase1_apollo/output/phase1_ranked_contacts.csv --enrich-emails
```

### Test on 5 Contacts
```bash
python main.py ../phase1_apollo/output/phase1_ranked_contacts.csv --max 5
```

### Only Enrich High-Value Contacts (Score 8+)
```bash
python main.py ../phase1_apollo/output/phase1_ranked_contacts.csv --min-score 8
```

## Output

Creates `phase2_enriched_TIMESTAMP.csv` in `output/` directory with additional columns:

- `real_email` - Enriched email from Apollo
- `real_email_status` - Email verification status
- `personal_research` - LinkedIn posts + profile summary
- `company_research` - Company intelligence from Perplexity
- `enrichment_errors` - Any errors during enrichment

## Module Structure

```
phase2_enrichment/
├── config.py              # Configuration & API keys
├── apify_enricher.py      # LinkedIn scraping via Apify
├── apollo_enricher.py     # Email enrichment via Apollo
├── company_researcher.py  # Company research via Perplexity
├── main.py                # Main orchestrator
├── output/                # Output CSVs
└── README.md              # This file
```

## API Keys Required

Set these in `../phase1_apollo/.env`:
```
APIFY_API_TOKEN=your_token
PERPLEXITY_API_KEY=your_key
APOLLO_API_KEY=your_key
```
