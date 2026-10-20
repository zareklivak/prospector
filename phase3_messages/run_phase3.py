"""
Wrapper script to run Phase 3 from subprocess
"""
import sys
import argparse
from main import Phase3Orchestrator
from config import USE_DUAL_LLMS

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Run Phase 3: Message Generation")
    parser.add_argument("input_csv", help="Path to Phase 2 output CSV")
    parser.add_argument("mode", choices=["email", "linkedin"], help="Message mode")
    parser.add_argument("--custom-template", help="Path to custom template JSON file (per-run override)")
    parser.add_argument("--min-profile-quality", type=int, default=None, help="Minimum profile quality score (1-10)")
    parser.add_argument("--company-type", help="Company type/vertical override (e.g., 'carrier', 'freight_broker', 'food_distributor')")
    parser.add_argument("--subject-line-style", choices=["question", "direct", "curiosity", "value", "custom"], default=None, help="Subject line generation style")
    parser.add_argument("--subject-line-prompt", help="Custom prompt for subject line generation (used with --subject-line-style custom)")

    args = parser.parse_args()

    # DEBUG LOGGING - use stdout and flush immediately
    print(f"\n🔧 DEBUG run_phase3.py:")
    print(f"   Input CSV: {args.input_csv}")
    print(f"   Mode: {args.mode}")
    print(f"   Custom template path: {args.custom_template}")
    if args.custom_template:
        import os
        print(f"   Template file exists: {os.path.exists(args.custom_template)}")
    if args.min_profile_quality:
        print(f"   Minimum profile quality: {args.min_profile_quality}")
    if args.company_type:
        print(f"   Company type override: {args.company_type}")
    if args.subject_line_style:
        print(f"   Subject line style: {args.subject_line_style}")
        if args.subject_line_prompt:
            print(f"   Subject line prompt: {args.subject_line_prompt[:50]}...")
    print("")
    sys.stdout.flush()

    # Build subject line config if specified
    subject_line_config = None
    if args.subject_line_style:
        subject_line_config = {
            "style": args.subject_line_style,
            "customPrompt": args.subject_line_prompt
        }

    # Run Phase 3
    orchestrator = Phase3Orchestrator(
        mode=args.mode,
        use_dual_llms=USE_DUAL_LLMS,
        custom_template_path=args.custom_template,
        company_type_override=args.company_type,
        subject_line_config=subject_line_config
    )

    df_with_messages = orchestrator.process_csv(
        input_csv=args.input_csv,
        mode=args.mode,
        max_contacts=None,
        min_score=None,
        min_profile_quality=args.min_profile_quality
    )

    # Export to CSV
    output_path = orchestrator.export_to_csv(
        df=df_with_messages,
        mode=args.mode
    )

    # Print output path for parent process to capture
    print(f"OUTPUT_PATH:{output_path}")

if __name__ == "__main__":
    main()
