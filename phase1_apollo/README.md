# Phase 1: Apollo Scraper & Lead Scorer

Automated prospecting pipeline that scrapes Apollo.io for Director+ contacts, scores them by role fit, and exports ranked CSVs.

## Features

- ✅ Scrapes Apollo.io for Director, VP, Head, and C-Suite contacts
- ✅ Filters for verified emails only (no credit waste on unverified contacts)
- ✅ Intelligent lead scoring based on role keywords (AI, ops, supply chain = high priority)
- ✅ Ranks and exports top N contacts per company
- ✅ Handles multiple companies in single run
- ✅ Clean CSV output ready for Phase 2 enrichment

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
Edit `config.py` and add your Apollo API key:
```python
APOLLO_API_KEY = "your_apollo_api_key_here"
```

### 3. Run the Scraper
```bash
python main.py
```

## Configuration

### Customize in `config.py`:
- **APOLLO_API_KEY**: Your Apollo.io API key
- **SCORING_KEYWORDS**: Adjust keyword scores (AI, operations, finance, etc.)
- **SENIORITIES**: Seniority levels to target (default: director, vp, head, c_suite)
- **DEFAULT_CONTACTS_TO_EXPORT**: How many top contacts per company (default: 20)
- **MAX_CONTACTS_PER_COMPANY**: Max to pull before scoring (default: 1000)

### Customize in `main.py`:
```python
company_domains = [
    "fedex.com",
    "ups.com",
    "dhl.com",
]

contacts_per_company = 50  # Export top 50 per company
max_initial_scrape = 1000  # Pull 1000 initially, then score
```

## Scoring System

Contacts are scored 1-10 based on role title keywords:

### High Priority (8-10)
- AI, Innovation, Transformation
- Supply Chain, Logistics, Operations

### Medium Priority (6-8)
- Strategy, Product, Engineering, IT

### Lower Priority (3-5)
- Finance, HR, Legal

**Bonus modifiers:**
- Chief/CXO: +2 points
- VP: +1 point
- Head: +1 point

## Output

CSV file with columns:
- Basic: first_name, last_name, title, email, email_status
- Contact: linkedin_url, city, state, country
- Company: company_name, company_domain, company_linkedin
- Scoring: fit_score (1-10), seniority, departments

**Output location:** `output/phase1_ranked_contacts_TIMESTAMP.csv`

## Example Output

```
Company: fedex.com
✓ Retrieved 847 contacts with verified emails
✓ Selected 20 top-ranked contacts

Top 5 contacts:
1. Sarah Chen - Chief Innovation Officer (Score: 10)
2. Michael Torres - VP of Supply Chain Operations (Score: 9)
3. Jennifer Park - Head of Logistics Technology (Score: 9)
4. David Kumar - Director of AI & Automation (Score: 10)
5. Lisa Wang - VP of Digital Transformation (Score: 9)
```

## Next Steps

Phase 1 output is ready for:
- **Phase 2**: Enrich with LinkedIn scraping (Apify) + company research (Perplexity/Claude)
- **Phase 3**: Generate personalized 4-step email/LinkedIn sequences

## Project Structure

```
phase1_apollo/
├── config.py              # API keys & scoring configuration
├── apollo_scraper.py      # Apollo.io API integration
├── lead_scorer.py         # Lead scoring logic
├── main.py                # Main orchestrator
├── requirements.txt       # Dependencies
├── README.md             # This file
└── output/               # CSV exports
```

## Troubleshooting

**"No contacts found"**
- Check if company domain is correct
- Verify company has Director+ employees in Apollo
- Check API key is valid

**"Few contacts with verified emails"**
- Normal for smaller companies
- Adjust `contact_email_status` in apollo_scraper.py to include "guessed"

**Scoring seems off**
- Adjust keywords in `config.py` SCORING_KEYWORDS
- Test with: `python lead_scorer.py`
