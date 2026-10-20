"""
Lead Scoring Module
Scores contacts based on their role titles using keyword matching
Uses JSON config for flexibility and word-boundary matching for accuracy
"""

import json
import re
import os
import pandas as pd


class LeadScorer:
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Default to config/scoring_config.json relative to this file
            config_path = os.path.join(
                os.path.dirname(__file__),
                "config",
                "scoring_config.json"
            )

        with open(config_path, 'r') as f:
            config = json.load(f)

        # Filter out comment keys (starting with _) and sort by length (longest first)
        # This ensures more specific phrases match before generic ones
        all_keywords = config['keyword_scores']
        self.keyword_scores = {
            k: v for k, v in all_keywords.items()
            if not k.startswith('_') and isinstance(v, (int, float))
        }

        # Sort keywords by length descending for longest-first matching
        self.keyword_scores = dict(
            sorted(self.keyword_scores.items(), key=lambda x: len(x[0]), reverse=True)
        )

        self.default_score = config.get('default_score', 1)

        print(f"✓ Lead scorer loaded with {len(self.keyword_scores)} keywords")

    def score_lead(self, title: str) -> int:
        """
        Score a lead based on their title.

        Uses word boundary matching for short keywords (<=3 chars) to avoid
        false positives like "ai" matching "claims".

        IMPORTANT: Score 0 acts as a VETO - if any exclusion keyword matches,
        the entire title gets score 0 regardless of other matches.

        Returns a score from 0-10.
        """
        if not title:
            return 0

        title_lower = title.lower()
        max_score = self.default_score
        has_exclusion = False

        # Check all keywords (longest first due to sorting)
        for keyword, score in self.keyword_scores.items():
            matched = False

            # Use word boundary matching for short keywords (<=3 chars)
            # to avoid false positives
            if len(keyword) <= 3:
                # Create regex pattern with word boundaries
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, title_lower):
                    matched = True
            else:
                # Use regular substring matching for longer keywords
                if keyword in title_lower:
                    matched = True

            if matched:
                if score == 0:
                    # Exclusion keyword found - veto this person
                    has_exclusion = True
                    # Don't break - continue to check if other exclusions match
                else:
                    # Take the highest score
                    max_score = max(max_score, score)

        # If any exclusion keyword matched, return 0 regardless of other scores
        if has_exclusion:
            return 0

        return max_score

    def score_leads_df(self, df, title_column='title'):
        """
        Add a 'fit_score' column to a pandas DataFrame
        """
        df['fit_score'] = df[title_column].apply(self.score_lead)
        return df

    def deduplicate_titles(self, df, max_per_title=10):
        """
        Limit the number of contacts with identical titles PER COMPANY to prevent
        over-representation of common roles like "Director of Operations".

        When a title appears more than max_per_title times at the same company,
        keep only the highest-scoring ones.
        """
        if df.empty:
            return df

        # Ensure df is sorted by fit_score descending first
        df = df.sort_values(by='fit_score', ascending=False).copy()

        # Group by company_domain + title and keep top N per group
        # This ensures we deduplicate per company, not globally
        df_deduplicated = df.groupby(
            ['company_domain', 'title'],
            group_keys=False
        ).apply(lambda x: x.nlargest(max_per_title, 'fit_score'))

        # Reset index after groupby
        df_deduplicated = df_deduplicated.reset_index(drop=True)

        # Re-sort to maintain overall score order
        df_deduplicated = df_deduplicated.sort_values(
            by=['fit_score', 'title'],
            ascending=[False, True]
        ).reset_index(drop=True)

        removed_count = len(df) - len(df_deduplicated)
        if removed_count > 0:
            print(f"   ⚡ Removed {removed_count} duplicate titles (max {max_per_title} per title per company)")

        return df_deduplicated

    def rank_and_filter(self, df, top_n=None, min_score=1, deduplicate=True, max_per_title=10):
        """
        Sort by fit_score and optionally take top N leads
        Filters out scores below min_score (default: 1)
        Optionally deduplicates titles to prevent over-representation
        """
        # Filter out low scores (including exclusions at 0)
        df_filtered = df[df['fit_score'] >= min_score].copy()

        # Sort by score (high to low), then by title alphabetically for consistency
        df_sorted = df_filtered.sort_values(
            by=['fit_score', 'title'],
            ascending=[False, True]
        ).reset_index(drop=True)

        # Deduplicate titles if requested
        if deduplicate:
            df_sorted = self.deduplicate_titles(df_sorted, max_per_title=max_per_title)

        if top_n:
            return df_sorted.head(top_n)

        return df_sorted


if __name__ == "__main__":
    # Test the scorer
    scorer = LeadScorer()

    test_titles = [
        # High-value titles (should score 9-10)
        "Chief AI Officer",
        "VP of Digital Transformation",
        "Head of Supply Chain Technology",
        "Director of Logistics Innovation",

        # Mid-value titles (should score 6-8)
        "Chief Operating Officer",
        "VP of Operations",
        "Director of Supply Chain",
        "Head of Warehouse Operations",

        # Lower value titles (should score 4-5)
        "CTO",
        "VP of IT",
        "Director of Analytics",

        # Excluded titles (should score 0)
        "CFO",
        "VP of Finance",
        "Director of Human Resources",
        "Chief Marketing Officer",
        "VP of Sales",
        "Director of Recruiting",

        # Edge cases
        "VP of AI and Machine Learning",  # Should be 10
        "Director of Digital Supply Chain and Operations",  # Should be 9
    ]

    print("\n" + "="*70)
    print("LEAD SCORER TEST - Enhanced Scoring System")
    print("="*70)
    print(f"{'Title':<55} {'Score':<6} {'Tier'}")
    print("-"*70)

    tier_labels = {
        10: "Tier 1 - AI/Innovation",
        9: "Tier 2 - Tech Logistics",
        8: "Tier 3 - Operations",
        7: "Tier 4 - Customer Ops",
        6: "Tier 5 - Core Logistics",
        5: "Tier 6 - IT/Tech",
        4: "Tier 7 - Analytics",
        1: "Default",
        0: "EXCLUDED"
    }

    for title in test_titles:
        score = scorer.score_lead(title)
        tier = tier_labels.get(score, f"Score {score}")

        # Color coding
        if score >= 9:
            icon = "🟢"
        elif score >= 7:
            icon = "🟡"
        elif score >= 4:
            icon = "🟠"
        elif score == 0:
            icon = "🔴"
        else:
            icon = "⚪"

        print(f"{title:<55} {score:<6} {tier} {icon}")

    print("\n" + "="*70)
    print("✓ Scoring test complete")
    print("="*70)
