# Phase 3: Message Generation

Generates highly personalized 4-step outreach sequences (email OR LinkedIn) using enriched prospect data from Phase 2.

## Overview

Phase 3 takes the enriched CSV from Phase 2 (with personal LinkedIn research and company intelligence) and generates personalized multi-touch sequences ready for import into sending tools (Hey Reach for email, LinkedIn for InMail).

## Input Requirements

- **Phase 2 Enriched CSV** with these columns:
  - Basic contact info: `first_name`, `last_name`, `title`, `company_name`, `fit_score`
  - Personal research: `personal_research` (LinkedIn profile summary and recent activity)
  - Company research: `company_research` (Company operations and initiatives)

## Output

Adds 4 new columns to the CSV:
- `message_1` - Initial outreach
- `message_2` - Follow-up #1 (2-3 days later)
- `message_3` - Follow-up #2 (4-5 days after message 2)
- `message_4` - Final follow-up (1 week after message 3)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure API keys are in `.env` file (in `phase1_apollo/`):
```
ANTHROPIC_API_KEY=your_key_here
```

## Usage

### Basic Usage

```bash
# Generate email sequences for all contacts
python main.py ../phase2_enrichment/output/phase2_enriched.csv

# Generate LinkedIn sequences
python main.py ../phase2_enrichment/output/phase2_enriched.csv --mode linkedin
```

### Test with Single Contact

```bash
# Test with 1 contact first
python main.py ../phase2_enrichment/output/phase2_enriched.csv --max 1
```

### Filter by Fit Score

```bash
# Only generate for high-value contacts (score >= 8)
python main.py ../phase2_enrichment/output/phase2_enriched.csv --min-score 8
```

## Configuration

Edit `config.py` to customize:

- **LLM Provider:** `claude` or `openai`
- **Model:** `claude-sonnet-4-5-20250929` or `gpt-4-turbo`
- **Temperature:** `0.7` (creativity level)
- **Message Mode:** `email` or `linkedin`
- **Quality Controls:** Generic phrase detection, length validation

## Message Quality Standards

All messages must meet **Tier 1 Personalization** standards:

✅ **DO:**
- Reference specific LinkedIn posts by topic
- Mention actual role responsibilities
- Connect to company initiatives
- Use authentic, human language
- Focus on THEM, not selling

❌ **DON'T:**
- Generic "I saw your profile" statements
- Broad industry platitudes
- Feature dumping
- Copy/paste LinkedIn posts verbatim
- Corporate jargon

## Message Sequence Strategy

**Message 1:** Personalized observation → Value connection → Soft ask
**Message 2:** Follow-up → Add new value → Make meeting easier
**Message 3:** Different angle → Direct value → Clear CTA
**Message 4:** Breakup → Provide value → Leave door open

## File Structure

```
phase3_messages/
├── config.py                    # Configuration and settings
├── message_generator.py         # Core generation logic
├── prompts/
│   ├── system_instructions.py  # Base LLM instructions
│   ├── email_prompts.py        # Email sequence templates
│   └── linkedin_prompts.py     # LinkedIn sequence templates
├── main.py                      # Orchestrator
├── requirements.txt             # Dependencies
└── output/                      # Generated CSVs
```

## Example Output

**Email Message 1 (to Director of Business Transformation at MSC):**

```
SUBJECT: RPA scaling at MSC

Hi Joshua,

Saw you've grown your business transformation team at MSC from managing RPA developers to now overseeing Process Automation, Business Application Development, and BI groups - impressive scope expansion over the past 4 years.

Given MSC's scale (150K employees across 155 countries), I imagine you're constantly balancing automation velocity with integration complexity. We work with carriers facing similar challenges around automating high-volume communication workflows without disrupting existing systems.

Would you be open to a brief conversation about how you're prioritizing automation opportunities across your different groups? Happy to share what we're seeing work well at other global carriers.

Best,
[Name]
```

## Quality Validation

Each message is automatically validated for:
- No generic phrases (100+ common ones flagged)
- Appropriate length (150-250 words for email, 100-150 for LinkedIn)
- Includes recipient's name
- Personalization elements present

Failed validations trigger automatic retries (up to 3 attempts).

## Next Steps

After generating messages:
1. **Review sample messages** for quality
2. **Import to sending tool:**
   - Email sequences → Hey Reach
   - LinkedIn sequences → LinkedIn/Sales Navigator
3. **Monitor performance** and refine prompts as needed

## Troubleshooting

**"Missing required columns" error:**
- Ensure you're using a Phase 2 enriched CSV (not Phase 1)

**Generic message warnings:**
- Check that `personal_research` and `company_research` columns have data
- Review prompts in `prompts/` directory

**API rate limits:**
- Reduce batch size with `--max` flag
- Add delays in `message_generator.py`

## Advanced

### Customize Prompts

Edit files in `prompts/` directory:
- `system_instructions.py` - Overall tone and guidelines
- `email_prompts.py` - Email sequence structure
- `linkedin_prompts.py` - LinkedIn sequence structure

### Switch LLM Provider

In `config.py`:
```python
LLM_PROVIDER = "openai"  # or "claude"
MODEL = "gpt-4-turbo"    # or "claude-sonnet-4-5"
```

### Adjust Quality Thresholds

In `config.py`:
```python
MIN_PERSONALIZATION_SCORE = 7  # Stricter = higher threshold
FLAG_GENERIC_PHRASES = True    # Enable/disable validation
```
