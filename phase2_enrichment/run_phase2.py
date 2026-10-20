"""
Wrapper script to run Phase 2 from subprocess
"""
import sys
from main import Phase2Orchestrator

def main():
    try:
        # Read config from command line
        if len(sys.argv) < 2:
            print("Usage: python run_phase2.py <input_csv> [OPTIONS]")
            print("\nOptions:")
            print("  --enrich-emails        Enrich & verify emails with Apollo + Instantly.ai")
            print("  --waterfall            Use waterfall enrichment (Apollo -> Hunter -> Findymail)")
            print("  --verify-employment    Verify contacts still work at target company (uses LinkedIn data)")
            print("  --skip-linkedin        Skip LinkedIn scraping (saves Apify credits)")
            print("  --skip-company-research  Skip company research (for email-only enrichment)")
            print("  --min-score N          Only process contacts with fit_score >= N")
            print("  --min-profile-quality N  Only keep contacts with profile_quality_score >= N (1-10)")
            print("  --max N                Limit to first N contacts (for testing)")
            print("\nExample:")
            print("  python run_phase2.py phase1_output.csv --enrich-emails --max 10 --min-score 7")
            print("  python run_phase2.py phase1_output.csv --enrich-emails --waterfall --verify-employment")
            sys.exit(1)

        input_csv = sys.argv[1]
        enrich_emails = "--enrich-emails" in sys.argv
        waterfall_enrichment = "--waterfall" in sys.argv
        verify_employment = "--verify-employment" in sys.argv
        skip_linkedin = "--skip-linkedin" in sys.argv
        skip_company_research = "--skip-company-research" in sys.argv
        min_score = 1
        min_profile_quality = None  # No profile quality filter by default
        max_contacts = None  # Process all contacts by default
        max_workers = 12  # Conservative limit for Apify (32 concurrent / 2 jobs per contact = 16, use 12 for safety)

        # Parse command line arguments
        for i, arg in enumerate(sys.argv):
            if arg == "--min-score" and i + 1 < len(sys.argv):
                min_score = int(sys.argv[i + 1])
            if arg == "--min-profile-quality" and i + 1 < len(sys.argv):
                min_profile_quality = int(sys.argv[i + 1])
            if arg == "--max" and i + 1 < len(sys.argv):
                max_contacts = int(sys.argv[i + 1])
                try:
                    print(f"🔧 Limiting to {max_contacts} contacts for testing")
                except (ValueError, IOError):
                    pass  # Suppress I/O errors when stdout is closed

        # Log enrichment mode
        if enrich_emails:
            if waterfall_enrichment:
                print(f"🌊 Email enrichment: Thorough mode (Apollo -> Hunter -> Findymail with Instantly verification)")
            else:
                print(f"⚡ Email enrichment: Fast mode (Apollo only with Instantly verification)")

        # Run Phase 2
        orchestrator = Phase2Orchestrator()

        enriched_df = orchestrator.enrich_contacts_batch_parallel(
            input_csv=input_csv,
            enrich_emails=enrich_emails,
            waterfall_enrichment=waterfall_enrichment,
            verify_current_employment=verify_employment,
            skip_linkedin=skip_linkedin,
            skip_company_research=skip_company_research,
            max_contacts=max_contacts,
            min_score=min_score,
            min_profile_quality=min_profile_quality,
            max_workers=max_workers
        )

        # Export to CSV
        output_path = orchestrator.export_enriched_csv(enriched_df)

        # Print output path for parent process to capture
        try:
            print(f"OUTPUT_PATH:{output_path}")
        except (ValueError, IOError):
            # Suppress I/O errors when stdout is closed (happens in subprocess mode)
            # The file was still created successfully, just can't print the path
            pass

        sys.exit(0)  # Explicit success exit

    except KeyboardInterrupt:
        print("\n⚠️  Phase 2 interrupted by user", file=sys.stderr)
        sys.exit(130)  # Standard exit code for Ctrl+C
    except Exception as e:
        print(f"\n{'='*80}", file=sys.stderr)
        print(f"❌ PHASE 2 FAILED", file=sys.stderr)
        print(f"{'='*80}", file=sys.stderr)
        print(f"Error: {str(e)}", file=sys.stderr)
        print(f"Error Type: {type(e).__name__}", file=sys.stderr)
        print(f"\nFull Traceback:", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        print(f"{'='*80}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
