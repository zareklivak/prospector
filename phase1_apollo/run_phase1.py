"""
Wrapper script to run Phase 1 from subprocess
"""
import sys
import json
import argparse
from main import Phase1Orchestrator
from config import DEFAULT_SENIORITIES, DEFAULT_MAX_INITIAL_SCRAPE

def main():
    parser = argparse.ArgumentParser(description="Run Phase 1: Apollo Contact Scraping")
    parser.add_argument("company_domains_json", help="JSON array of company domains")
    parser.add_argument("contacts_per_company", type=int, help="Number of contacts to export per company")
    parser.add_argument("--include-all-contacts", action="store_true",
                        help="Include contacts without emails (for Phase 2 waterfall enrichment)")
    parser.add_argument("--seniorities", type=str, default=None, help="JSON array of seniority levels")
    parser.add_argument("--max-initial-scrape", type=int, default=DEFAULT_MAX_INITIAL_SCRAPE,
                        help="Maximum contacts to scrape before scoring")
    parser.add_argument("--min-score", type=int, default=1,
                        help="Minimum ICP fit score to include in output (1-10)")
    parser.add_argument("--include-unverified", action="store_true",
                        help="Include contacts without verified/guessed emails")

    args = parser.parse_args()

    company_domains = json.loads(args.company_domains_json)
    contacts_per_company = args.contacts_per_company
    max_initial_scrape = args.max_initial_scrape

    # Parse seniorities if provided
    seniorities = DEFAULT_SENIORITIES
    if args.seniorities:
        seniorities = json.loads(args.seniorities)
        print(f"📋 Using custom seniorities: {', '.join(seniorities)}")

    if args.include_all_contacts:
        print(f"🌊 Including all contacts for Phase 2 email enrichment")

    # Log min_score filter if non-default
    if args.min_score > 1:
        print(f"🎯 Min ICP score filter: {args.min_score}+")

    if args.include_unverified:
        print(f"📧 Including contacts without verified emails (LinkedIn-only mode)")

    # Run Phase 1
    orchestrator = Phase1Orchestrator(
        seniorities=seniorities,
        include_all_contacts=args.include_all_contacts,
        min_score=args.min_score,
        include_unverified=args.include_unverified
    )

    df_results = orchestrator.process_multiple_companies(
        company_domains=company_domains,
        contacts_per_company=contacts_per_company,
        max_initial_scrape=max_initial_scrape
    )

    # Export to CSV
    output_path = orchestrator.export_to_csv(df_results)

    # Print output path for parent process to capture
    print(f"OUTPUT_PATH:{output_path}")

if __name__ == "__main__":
    main()
