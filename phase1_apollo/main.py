"""
Phase 1 Main Orchestrator
Scrapes Apollo, scores leads, and exports ranked CSVs
"""

import os
import pandas as pd
from datetime import datetime
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from apollo_scraper import ApolloScraper
from lead_scorer import LeadScorer
from config import DEFAULT_CONTACTS_TO_EXPORT, MAX_CONTACTS_PER_COMPANY, DEFAULT_SENIORITIES

# Parallelization settings
MAX_COMPANY_WORKERS = 3  # Process up to 3 companies in parallel


class Phase1Orchestrator:
    def __init__(self, seniorities: List[str] = None, include_all_contacts: bool = False, min_score: int = 1, include_unverified: bool = False):
        """
        Phase 1 Orchestrator - Scrapes Apollo and scores leads.

        Email enrichment is handled in Phase 2 via waterfall (Apollo -> Hunter -> Findymail).

        Args:
            seniorities: List of seniority levels to filter by
            include_all_contacts: If True, include contacts without emails (for Phase 2 enrichment)
            min_score: Minimum ICP score to include
            include_unverified: If True, include contacts without verified/guessed emails
        """
        self.seniorities = seniorities if seniorities else DEFAULT_SENIORITIES
        self.include_all_contacts = include_all_contacts
        self.min_score = min_score
        self.include_unverified = include_unverified
        self.scraper = ApolloScraper(seniorities=self.seniorities, include_all_contacts=include_all_contacts)
        self.scorer = LeadScorer()
    
    def process_single_company(
        self,
        company_domain: str,
        contacts_to_export: int = DEFAULT_CONTACTS_TO_EXPORT,
        max_initial_scrape: int = MAX_CONTACTS_PER_COMPANY
    ) -> pd.DataFrame:
        """
        Process a single company through the full Phase 1 pipeline
        """
        print(f"\n🔍 Scraping {company_domain}...")

        # Step 1: Scrape Apollo
        df = self.scraper.scrape_company(company_domain, max_results=max_initial_scrape)

        if df.empty:
            print(f"⚠️  No contacts found for {company_domain}")
            return pd.DataFrame()

        # Step 2: Score leads
        df = self.scorer.score_leads_df(df)

        # Step 3: Rank and filter top N (with min_score filter)
        df_ranked = self.scorer.rank_and_filter(df, top_n=contacts_to_export, min_score=self.min_score)

        # Keep both verified and guessed emails - guessed can be verified later in Phase 2
        # Skip this filter when include_all_contacts is enabled (for Phase 2 waterfall enrichment)
        # Also skip when include_unverified is set (for LinkedIn-only outreach)
        if not self.include_all_contacts and not self.include_unverified:
            df_ranked = df_ranked[df_ranked['email_status'].isin(['verified', 'guessed'])].reset_index(drop=True)

        print(f"✅ Found {len(df_ranked)} high-quality contacts at {company_domain}")

        return df_ranked
    
    def process_multiple_companies(
        self,
        company_domains: List[str],
        contacts_per_company: int = DEFAULT_CONTACTS_TO_EXPORT,
        max_initial_scrape: int = MAX_CONTACTS_PER_COMPANY,
        parallel: bool = True
    ) -> pd.DataFrame:
        """
        Process multiple companies and combine into single CSV.

        Args:
            parallel: If True, process companies in parallel (faster but uses more resources)
        """
        all_results = []

        print(f"\n🚀 PHASE 1: Apollo Contact Scraping")
        print(f"📋 Processing {len(company_domains)} companies, targeting {contacts_per_company} contacts each")
        if parallel:
            print(f"⚡ Parallel mode: up to {MAX_COMPANY_WORKERS} companies at a time\n")
        else:
            print(f"🔄 Sequential mode\n")

        if parallel and len(company_domains) > 1:
            # Parallel processing with ThreadPoolExecutor
            completed = 0
            total = len(company_domains)

            def process_company(domain: str) -> Tuple[str, pd.DataFrame]:
                """Helper function for parallel company processing"""
                df = self.process_single_company(
                    domain,
                    contacts_to_export=contacts_per_company,
                    max_initial_scrape=max_initial_scrape
                )
                return domain, df

            with ThreadPoolExecutor(max_workers=MAX_COMPANY_WORKERS) as executor:
                futures = {
                    executor.submit(process_company, domain): domain
                    for domain in company_domains
                }

                for future in as_completed(futures):
                    domain, df = future.result()
                    completed += 1
                    print(f"\n[{completed}/{total}] Completed {domain}")

                    if not df.empty:
                        all_results.append(df)
        else:
            # Sequential processing (original behavior)
            for i, domain in enumerate(company_domains, 1):
                print(f"\n[{i}/{len(company_domains)}] ", end='')

                df = self.process_single_company(
                    domain,
                    contacts_to_export=contacts_per_company,
                    max_initial_scrape=max_initial_scrape
                )

                if not df.empty:
                    all_results.append(df)

        # Combine all results
        if all_results:
            combined_df = pd.concat(all_results, ignore_index=True)
            print(f"\n✅ Phase 1 Complete!")
            print(f"📊 Scraped {len(combined_df)} qualified contacts from {len(all_results)} companies")
            return combined_df
        else:
            print(f"\n❌ No contacts found for any companies")
            return pd.DataFrame()
    
    def export_to_csv(self, df: pd.DataFrame, filename: str = None) -> str:
        """
        Export DataFrame to CSV
        """
        if df.empty:
            print("⚠️  No data to export")
            return None
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"phase1_ranked_contacts_{timestamp}.csv"

        # Use relative path to output directory
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        df.to_csv(filepath, index=False)

        print(f"💾 Saved results to: {filename}")

        return filepath


def main():
    """
    Main execution function
    """
    # Initialize orchestrator
    orchestrator = Phase1Orchestrator()
    
    # Process 4 companies for email outreach
    company_domains = [
        "slpa.lk",
        "tcdd.gov.tr",
        "angloeastern.com",
        "fortrexsolutions.com",
    ]

    # Customize settings
    contacts_per_company = 50  # How many top contacts to export per company
    max_initial_scrape = 2000  # How many to pull initially before scoring
    
    # Process companies
    df_results = orchestrator.process_multiple_companies(
        company_domains=company_domains,
        contacts_per_company=contacts_per_company,
        max_initial_scrape=max_initial_scrape
    )
    
    # Export results
    if not df_results.empty:
        orchestrator.export_to_csv(df_results)
        
        print(f"\n\n🎉 Phase 1 Complete!")
        print(f"   Ready for Phase 2: Enrichment & Research")
    else:
        print(f"\n\n⚠️  No results to export")


if __name__ == "__main__":
    main()
