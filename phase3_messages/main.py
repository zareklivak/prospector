"""
Phase 3 Main Orchestrator
Generates personalized 4-step outreach sequences
"""

import sys
import os
import pandas as pd
from datetime import datetime
from typing import Optional
import time

from batch_message_generator import BatchMessageGenerator
from config import OUTPUT_DIR, MESSAGE_MODE, USE_DUAL_LLMS, CLAUDE_WORKERS, OPENAI_WORKERS
from concurrent.futures import ThreadPoolExecutor, as_completed


class Phase3Orchestrator:
    """
    Orchestrates message generation for enriched contacts
    DUAL LLM SUPPORT: Can use Claude and OpenAI in parallel!
    """

    def __init__(self, mode: str = MESSAGE_MODE, use_dual_llms: bool = USE_DUAL_LLMS, custom_template_path: Optional[str] = None, company_type_override: Optional[str] = None, subject_line_config: Optional[dict] = None):
        self.mode = mode  # "email" or "linkedin"
        self.use_dual_llms = use_dual_llms
        self.custom_template_path = custom_template_path
        self.company_type_override = company_type_override  # Store for logging/debugging
        self.subject_line_config = subject_line_config  # Subject line generation config

        # Initialize generators for both LLMs if dual mode enabled
        if use_dual_llms:
            self.claude_generator = BatchMessageGenerator(llm_provider="claude", custom_template_path=custom_template_path, subject_line_config=subject_line_config)
            self.openai_generator = BatchMessageGenerator(llm_provider="openai", custom_template_path=custom_template_path, subject_line_config=subject_line_config)
        else:
            self.generator = BatchMessageGenerator(llm_provider="claude", custom_template_path=custom_template_path, subject_line_config=subject_line_config)

    def process_csv(
        self,
        input_csv: str,
        mode: Optional[str] = None,
        max_contacts: Optional[int] = None,
        min_score: Optional[int] = None,
        min_profile_quality: Optional[int] = None,
        company_type_override: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Process Phase 2 CSV and generate messages for all contacts

        Args:
            input_csv: Path to Phase 2 enriched CSV
            mode: "email" or "linkedin" (overrides default)
            max_contacts: Limit number of contacts to process (for testing)
            min_score: Only process contacts with fit_score >= this value
            min_profile_quality: Only process contacts with profile_quality_score >= this value
            company_type_override: Optional industry override for testing
                                   (e.g., "broker", "carrier", "air freight")

        Returns:
            DataFrame with original data + message columns
        """

        mode = mode or self.mode

        print(f"\n🚀 PHASE 3: Message Generation ({mode.upper()} mode)")

        # Load Phase 2 CSV
        df = pd.read_csv(input_csv)
        print(f"📂 Loading {len(df)} enriched contacts...")

        # Apply filters
        if min_score:
            df = df[df['fit_score'] >= min_score]
            print(f"🎯 Filtering to {len(df)} high-scoring contacts (fit_score >= {min_score})")

        if min_profile_quality and min_profile_quality > 1:
            # Filter by profile quality score (only if > 1, since 1 means "no filtering")
            if 'profile_quality_score' in df.columns:
                original_count = len(df)
                df = df[df['profile_quality_score'] >= min_profile_quality]
                filtered_out = original_count - len(df)
                if filtered_out > 0:
                    print(f"🎯 Filtered out {filtered_out} contacts with profile_quality_score < {min_profile_quality}")
                    print(f"   Remaining: {len(df)} contacts with high-quality LinkedIn profiles")
            else:
                print(f"⚠️  Warning: profile_quality_score column not found. Skipping profile quality filter.")

        if max_contacts:
            df = df.head(max_contacts)

        if len(df) == 0:
            print("\n❌ No contacts to process after filtering")
            return df

        # Verify required columns
        required_cols = ['first_name', 'last_name', 'title', 'company_name',
                        'fit_score', 'personal_research', 'company_research']
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            print(f"\n❌ Missing required columns: {', '.join(missing_cols)}")
            print(f"   This doesn't look like a Phase 2 enriched CSV")
            return pd.DataFrame()

        # Show industry override message if provided
        if company_type_override:
            print(f"🎯 Using industry override: {company_type_override}")
            print(f"   All contacts will use {company_type_override} use cases")

        print(f"✉️  Generating personalized {mode} sequences for {len(df)} contacts...")
        sys.stdout.flush()

        start_time = time.time()

        def process_contact(idx_row, generator, llm_name):
            idx, row = idx_row
            contact_start = time.time()
            contact_name = f"{row['first_name']} {row['last_name']}"

            try:
                # Generate all 4 messages in ONE API call
                messages = generator.generate_batch_sequence(
                    row,
                    mode=mode,
                    company_type_override=company_type_override
                )
                elapsed = time.time() - contact_start
                return idx, messages, None, elapsed, contact_name, llm_name
            except Exception as e:
                elapsed = time.time() - contact_start
                return idx, None, str(e), elapsed, contact_name, llm_name

        # Process contacts in parallel
        completed = 0
        errors = 0
        total_api_time = 0

        if self.use_dual_llms:
            # DUAL LLM MODE: Split contacts 50/50 between Claude and OpenAI
            midpoint = len(df) // 2
            claude_contacts = [(idx, row) for idx, row in df.iloc[:midpoint].iterrows()]
            openai_contacts = [(idx, row) for idx, row in df.iloc[midpoint:].iterrows()]

            print(f"🤖 Using dual AI: Claude Sonnet 4.5 + OpenAI GPT-4o ({CLAUDE_WORKERS + OPENAI_WORKERS} parallel workers)")
            sys.stdout.flush()

            # Create futures for both LLMs
            futures = {}
            with ThreadPoolExecutor(max_workers=CLAUDE_WORKERS) as claude_executor, \
                 ThreadPoolExecutor(max_workers=OPENAI_WORKERS) as openai_executor:

                # Submit Claude tasks
                for contact in claude_contacts:
                    future = claude_executor.submit(process_contact, contact, self.claude_generator, "Claude")
                    futures[future] = contact[0]

                # Submit OpenAI tasks
                for contact in openai_contacts:
                    future = openai_executor.submit(process_contact, contact, self.openai_generator, "OpenAI")
                    futures[future] = contact[0]

                # Process results as they complete
                for future in as_completed(futures):
                    idx, messages, error, elapsed, contact_name, llm_name = future.result()
                    total_api_time += elapsed

                    if error:
                        errors += 1
                        for msg_num in range(1, 5):
                            df.at[idx, f'message_{msg_num}'] = f"ERROR: {error}"
                        df.at[idx, 'generated_by'] = llm_name
                        if self.subject_line_config:
                            df.at[idx, 'subject_line'] = f"ERROR: {error}"
                    else:
                        for msg_num in range(1, 5):
                            df.at[idx, f'message_{msg_num}'] = messages[f'message_{msg_num}']
                        df.at[idx, 'generated_by'] = llm_name
                        # Add subject line if present
                        if 'subject_line' in messages:
                            df.at[idx, 'subject_line'] = messages['subject_line']

                    completed += 1

                    # Show progress every 10 contacts or at completion
                    if completed % 10 == 0 or completed == len(df):
                        elapsed_total = time.time() - start_time
                        avg_time = elapsed_total / completed if completed > 0 else 0
                        remaining = len(df) - completed
                        eta = avg_time * remaining

                        progress_pct = int(completed/len(df)*100)
                        print(f"📝 Generated {completed}/{len(df)} sequences ({progress_pct}%) | ETA: {eta:.0f}s", flush=True)

        else:
            # SINGLE LLM MODE: Use only Claude
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {executor.submit(process_contact, (idx, row), self.generator, "Claude"): idx for idx, row in df.iterrows()}

                for future in as_completed(futures):
                    idx, messages, error, elapsed, contact_name, llm_name = future.result()
                    total_api_time += elapsed

                    if error:
                        errors += 1
                        for msg_num in range(1, 5):
                            df.at[idx, f'message_{msg_num}'] = f"ERROR: {error}"
                        if self.subject_line_config:
                            df.at[idx, 'subject_line'] = f"ERROR: {error}"
                    else:
                        for msg_num in range(1, 5):
                            df.at[idx, f'message_{msg_num}'] = messages[f'message_{msg_num}']
                        # Add subject line if present
                        if 'subject_line' in messages:
                            df.at[idx, 'subject_line'] = messages['subject_line']

                    completed += 1

                    # Show progress every 10 contacts or at completion
                    if completed % 10 == 0 or completed == len(df):
                        elapsed_total = time.time() - start_time
                        avg_time = elapsed_total / completed if completed > 0 else 0
                        remaining = len(df) - completed
                        eta = avg_time * remaining

                        progress_pct = int(completed/len(df)*100)
                        print(f"📝 Generated {completed}/{len(df)} sequences ({progress_pct}%) | ETA: {eta:.0f}s", flush=True)

        total_time = time.time() - start_time
        avg_time_per_contact = total_time / len(df) if len(df) > 0 else 0

        # Estimate cost (rough estimate: ~2000 input + 1500 output tokens per contact)
        estimated_input_tokens = len(df) * 2000
        estimated_output_tokens = len(df) * 1500
        estimated_cost = (estimated_input_tokens / 1_000_000 * 3) + (estimated_output_tokens / 1_000_000 * 15)

        print(f"\n✅ Phase 3 Complete!")
        print(f"📊 Generated {len(df) - errors} sequences in {total_time/60:.1f} minutes")
        if errors > 0:
            print(f"⚠️  {errors} sequences failed")
        print(f"💰 Estimated cost: ${estimated_cost:.2f}")
        sys.stdout.flush()

        return df

    def export_to_csv(self, df: pd.DataFrame, mode: str, filename: Optional[str] = None) -> str:
        """
        Export DataFrame with generated messages to CSV

        Args:
            df: DataFrame with messages
            mode: "email" or "linkedin"
            filename: Custom filename (optional)

        Returns:
            Path to exported file
        """

        if df.empty:
            print("\n⚠️  No data to export")
            return None

        # Generate filename
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"phase3_messages_{mode}_{timestamp}.csv"

        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Full path
        filepath = os.path.join(OUTPUT_DIR, filename)

        # Export
        df.to_csv(filepath, index=False)

        print(f"💾 Saved to: {filename}")

        return filepath


def main():
    """
    Main execution function
    """

    print(f"\n{'#'*80}")
    print(f"PHASE 3: MESSAGE GENERATION")
    print(f"{'#'*80}\n")

    # Check for input file
    if len(sys.argv) < 2:
        print("Usage: python main.py <phase2_csv_file> [OPTIONS]")
        print("\nOptions:")
        print("  --mode [email|linkedin]           Message type (default: email)")
        print("  --max N                           Limit to N contacts (for testing)")
        print("  --min-score N                     Only process contacts with fit_score >= N")
        print("  --min-profile-quality N           Only process contacts with profile_quality_score >= N (1-10)")
        print("  --custom-template PATH            Path to custom template JSON file")
        print("\nExamples:")
        print("  python main.py ../phase2_enrichment/output/phase2_enriched.csv")
        print("  python main.py ../phase2_enrichment/output/phase2_enriched.csv --mode linkedin")
        print("  python main.py ../phase2_enrichment/output/phase2_enriched.csv --max 10")
        print("  python main.py ../phase2_enrichment/output/phase2_enriched.csv --min-score 8")
        print("  python main.py ../phase2_enrichment/output/phase2_enriched.csv --min-profile-quality 6")
        print("  python main.py ../phase2_enrichment/output/phase2_enriched.csv --min-score 7 --min-profile-quality 6")
        print("  python main.py ../phase2_enrichment/output/phase2_enriched.csv --custom-template ./templates/my_template.json")
        sys.exit(1)

    input_csv = sys.argv[1]
    mode = MESSAGE_MODE  # Default from config
    max_contacts = None
    min_score = None
    min_profile_quality = None
    custom_template_path = None

    # Parse args
    for i, arg in enumerate(sys.argv):
        if arg == "--mode" and i + 1 < len(sys.argv):
            mode = sys.argv[i + 1]
        if arg == "--max" and i + 1 < len(sys.argv):
            max_contacts = int(sys.argv[i + 1])
        if arg == "--min-score" and i + 1 < len(sys.argv):
            min_score = int(sys.argv[i + 1])
        if arg == "--min-profile-quality" and i + 1 < len(sys.argv):
            min_profile_quality = int(sys.argv[i + 1])
        if arg == "--custom-template" and i + 1 < len(sys.argv):
            custom_template_path = sys.argv[i + 1]

    # Validate mode
    if mode not in ["email", "linkedin"]:
        print(f"❌ Invalid mode: {mode}. Must be 'email' or 'linkedin'")
        sys.exit(1)

    # Run message generation
    orchestrator = Phase3Orchestrator(mode=mode, custom_template_path=custom_template_path)

    df_with_messages = orchestrator.process_csv(
        input_csv=input_csv,
        mode=mode,
        max_contacts=max_contacts,
        min_score=min_score,
        min_profile_quality=min_profile_quality
    )

    # Export results
    if not df_with_messages.empty:
        orchestrator.export_to_csv(df_with_messages, mode)
        print(f"\n\n🎉 Phase 3 Complete!")
        print(f"   Generated {mode} sequences for {len(df_with_messages)} contacts")
        print(f"   Ready for import to sending tools!")
    else:
        print(f"\n\n⚠️  No messages generated")


if __name__ == "__main__":
    main()
