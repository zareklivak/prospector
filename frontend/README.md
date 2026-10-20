# Prospector - Frontend

React/TypeScript frontend for the Prospector pipeline built with Lovable.

## Features

### Pipeline Configuration
- **Company Domains Input:** Add one or more company domains to prospect
- **Contacts Per Company:** Set how many contacts to scrape per domain
- **Message Mode:** Choose between Email or LinkedIn outreach sequences

### Email Enrichment & Verification
- **Enrich Emails (Apollo):** Get real, verified email addresses from Apollo.io
- **Double Verify with Instantly.ai:** Additional email verification layer that reduces bounce rates
  - Only enabled when email enrichment is checked
  - Validates emails in real-time using Instantly.ai's verification API
  - Filters out invalid/risky emails automatically (catch-all, disposable, role-based)
  - Improves email deliverability and sender reputation
  - Cost: ~$0.01 per email verified
  - Adds `instantly_verified` column to output CSVs

### Filtering Options
- **Min ICP Score (1-10):** Filter by title/role fit
- **Min Profile Quality (1-10):** Filter by LinkedIn profile completeness
- **Prospect-Only Mode:** Skip enrichment & messages, export raw contact lists

### Message Templates
- **Template Library:** Pre-built industry-specific templates
- **Live Preview:** See exactly how messages will look
- **Easy Editing:** Modify templates with instant preview updates
- **Auto-Save:** Templates preserved when switching tabs

### Real-Time Progress
- **Live Pipeline Updates:** WebSocket-powered progress tracking
- **Stage Indicators:** Know exactly which phase is running
- **Cost Tracking:** See costs accumulate in real-time
- **Error Handling:** Clear error messages if something fails

## How the Frontend Works with Instantly.ai

Instantly.ai email verification adds a second layer of validation after Apollo enrichment. While Apollo provides emails, Instantly.ai checks if they're actually deliverable in real-time. This prevents bounces and protects your sender reputation.

**What gets filtered out:**
- Invalid emails (non-existent addresses)
- Risky emails (catch-all domains, disposable emails)
- Role-based emails (info@, support@, etc.)
- Temporary/spam trap addresses

**Result:** Only high-quality, deliverable emails make it to your final CSV.

### Email Verification Checkbox

The "Double verify with Instantly.ai" checkbox:
- **Location:** Indented under "Enrich emails (Apollo)"
- **Dependency:** Automatically disabled when enrichment is unchecked
- **Auto-unchecks:** When you uncheck enrichment, verification unchecks too
- **When to use:** Enable for cold email campaigns where deliverability matters
- **Frontend file:** `src/components/CompanyInputSection.tsx`

### State Management

The frontend tracks verification with the `verifyEmails` state:

```typescript
const [verifyEmails, setVerifyEmails] = useState(false);
```

This state is passed to the backend API:

```typescript
{
  company_domains: domains,
  enrich_emails: enrichEmails,
  verify_emails: verifyEmails,  // ← Sent to backend
  // ... other config
}
```

### Backend Integration

The backend receives `verify_emails` and:
1. Passes `--verify-emails` flag to Phase 1 (prospect-only) or Phase 2 (full pipeline)
2. Instantly.ai verification runs after Apollo enrichment
3. Invalid/risky emails are filtered out
4. CSV output includes `instantly_verified` column showing verification status

### CSV Output Column

All final CSVs include the `instantly_verified` column:

| Value | Meaning |
|-------|---------|
| `verified` | Email passed Instantly.ai verification - safe to send ✅ |
| `not_verified` | Verification was not enabled or email was not enriched |

**Note:** When verification is enabled, contacts with invalid/risky emails are automatically removed from the CSV. You'll only see rows with `instantly_verified = "verified"` in the output.

This column appears in:
- **Phase 1 output** (prospect-only mode with verification)
- **Phase 2 output** (full pipeline with verification)
- **Phase 3 output** (final output with messages)

**Use in Instantly.ai:** Import the CSV with verified emails directly into Instantly.ai for your campaigns. The verification is already done!

## Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on: http://localhost:5173  
Backend API: http://localhost:8000

## File Structure

```
frontend/src/
├── components/
│   ├── CompanyInputSection.tsx    # Email verification checkbox
│   ├── TemplateEditor.tsx         # Message template editor
│   └── PipelineProgress.tsx       # Real-time progress display
├── pages/
│   └── Index.tsx                  # Main app page
└── hooks/
    └── use-toast.ts               # Toast notifications
```

## Key Components

### CompanyInputSection.tsx

Handles all pipeline configuration including:
- Company domain input
- Email enrichment toggle
- **Email verification toggle** (new!)
- Prospect-only mode
- ICP score filter
- Profile quality filter

**Instantly.ai Integration:**
```tsx
{/* Email Enrichment Options */}
<div className="space-y-3">
  <div className="flex items-center space-x-3">
    <Checkbox 
      id="enrich"
      checked={enrichEmails}
      onCheckedChange={(checked) => {
        setEnrichEmails(checked);
        if (!checked) setVerifyEmails(false);  // Auto-uncheck verification
      }}
    />
    <Label>Enrich emails (Apollo)</Label>
  </div>

  {/* Verification checkbox - indented */}
  <div className="flex items-center space-x-3 ml-8">
    <Checkbox
      id="verify"
      checked={verifyEmails}
      disabled={!enrichEmails}  // Disabled when enrichment off
      onCheckedChange={(checked) => setVerifyEmails(checked)}
    />
    <Label>Double verify with Instantly.ai</Label>
  </div>
</div>
```

### Index.tsx

Main orchestrator that:
- Manages all state
- Calls backend API with configuration
- Handles WebSocket connection for progress
- Displays results and errors

## Environment Variables

The frontend doesn't need environment variables (API keys are backend-only).

## Styling

Uses **shadcn/ui** components with custom Waypoint branding:
- Primary: `brand-navy` (#0A2647)
- Accent: `brand-cargo-orange` (#E17B37)
- Background: `brand-cargo-khaki` (#C9AE74)

## Testing

To test email verification in the UI:

1. Start backend: `python3 start_server.py`
2. Start frontend: `cd frontend && npm run dev`
3. Open browser to http://localhost:5173
4. Enter company domain (e.g., "bnsf.com")
5. Check "Enrich emails (Apollo)"
6. Check "Double verify with Instantly.ai"
7. Click "Run Pipeline"
8. Watch verification happen in real-time
9. Download CSV with `instantly_verified` column

## Documentation

See `/CLAUDE.md` in project root for complete documentation on:
- Instantly.ai email verification
- API integration details
- Cost structure
- Troubleshooting

## Support

For frontend issues:
- Check browser console for errors
- Verify backend is running on port 8000
- Check WebSocket connection in Network tab

For verification issues:
- See main CLAUDE.md documentation
- Check backend logs
- Verify `INSTANTLY_API_KEY` in `.env`
