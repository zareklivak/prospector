"""
Employment Verifier
Verifies that contacts are still employed at the target company
by analyzing LinkedIn personal_research data.

Uses fuzzy string matching to compare the company name from Apollo
with the "Current Position" extracted from LinkedIn profile scraping.
"""

import re
from typing import Tuple, Optional
from difflib import SequenceMatcher


class EmploymentVerifier:
    """
    Verifies contact employment status by comparing Apollo company data
    with LinkedIn Current Position information.
    """

    def __init__(self, similarity_threshold: float = 0.6):
        """
        Initialize the employment verifier.

        Args:
            similarity_threshold: Minimum similarity score (0-1) for company names
                                  to be considered a match. Default 0.6 allows for
                                  variations like "Genesis Energy" vs "Genesis Energy, L.P."
        """
        self.similarity_threshold = similarity_threshold

    def normalize_company_name(self, name: str) -> str:
        """
        Normalize a company name for comparison by:
        - Converting to lowercase
        - Removing common suffixes (Inc, LLC, L.P., Corp, etc.)
        - Removing punctuation
        - Stripping extra whitespace

        Args:
            name: Raw company name

        Returns:
            Normalized company name for comparison
        """
        if not name:
            return ""

        # Convert to lowercase
        normalized = name.lower().strip()

        # Remove common corporate suffixes
        suffixes = [
            r'\s*,?\s*(inc\.?|incorporated)$',
            r'\s*,?\s*(llc|l\.l\.c\.)$',
            r'\s*,?\s*(l\.p\.|lp|limited partnership)$',
            r'\s*,?\s*(ltd\.?|limited)$',
            r'\s*,?\s*(corp\.?|corporation)$',
            r'\s*,?\s*(co\.?|company)$',
            r'\s*,?\s*(plc)$',
            r'\s*,?\s*(gmbh)$',
            r'\s*,?\s*(s\.a\.|sa)$',
            r'\s*,?\s*(n\.v\.|nv)$',
            r'\s*,?\s*(group|holdings?)$',
            r'\s*,?\s*(international|intl\.?)$',
        ]

        for suffix in suffixes:
            normalized = re.sub(suffix, '', normalized, flags=re.IGNORECASE)

        # Remove punctuation (except spaces)
        normalized = re.sub(r'[^\w\s]', '', normalized)

        # Collapse multiple spaces
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        return normalized

    def calculate_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two company names using SequenceMatcher.

        Args:
            name1: First company name
            name2: Second company name

        Returns:
            Similarity score between 0 and 1
        """
        norm1 = self.normalize_company_name(name1)
        norm2 = self.normalize_company_name(name2)

        if not norm1 or not norm2:
            return 0.0

        # Use SequenceMatcher for fuzzy comparison
        return SequenceMatcher(None, norm1, norm2).ratio()

    def extract_current_position_company(self, personal_research: str) -> Optional[str]:
        """
        Extract the company name from the **Current Position:** field
        in the personal_research text.

        Expected format: "**Current Position:** {title} at {company} ({duration})"

        Args:
            personal_research: The personal_research text from LinkedIn scrape

        Returns:
            Company name from Current Position, or None if not found
        """
        if not personal_research:
            return None

        # Look for **Current Position:** pattern
        # Format: "**Current Position:** CTO at MasterCo Internationals (16 yrs)"
        pattern = r'\*\*Current Position:\*\*\s*(.+?)(?:\n|$)'
        match = re.search(pattern, personal_research)

        if not match:
            return None

        position_text = match.group(1).strip()

        # Extract company name - it comes after " at " and before optional duration in parentheses
        # Pattern: "{title} at {company} ({duration})" or "{title} at {company}"
        at_pattern = r'\s+at\s+(.+?)(?:\s*\([^)]+\)\s*)?$'
        at_match = re.search(at_pattern, position_text, re.IGNORECASE)

        if at_match:
            company = at_match.group(1).strip()
            # Remove any trailing parenthetical duration if still present
            company = re.sub(r'\s*\([^)]*\)\s*$', '', company).strip()
            return company

        return None

    def verify_employment(
        self,
        target_company: str,
        personal_research: str
    ) -> Tuple[bool, str, Optional[str], float]:
        """
        Verify that the contact is currently employed at the target company.

        Args:
            target_company: The company name from Apollo (the company we're targeting)
            personal_research: The personal_research text containing LinkedIn data

        Returns:
            Tuple of:
            - is_verified: True if contact appears to still work at target company
            - status: One of "verified", "mismatch", "unknown"
            - current_company: The company extracted from LinkedIn (or None)
            - similarity_score: The similarity score between companies (0-1)
        """
        # Extract current company from LinkedIn
        current_company = self.extract_current_position_company(personal_research)

        if not current_company:
            # Can't verify - no Current Position data found
            return True, "unknown", None, 0.0

        if not target_company:
            # No target company to compare against
            return True, "unknown", current_company, 0.0

        # Calculate similarity
        similarity = self.calculate_similarity(target_company, current_company)

        if similarity >= self.similarity_threshold:
            return True, "verified", current_company, similarity
        else:
            return False, "mismatch", current_company, similarity

    def filter_verified_contacts(
        self,
        df,
        target_company_col: str = "company_name",
        personal_research_col: str = "personal_research"
    ) -> Tuple:
        """
        Filter a DataFrame to only include contacts verified as still employed
        at the target company.

        Args:
            df: pandas DataFrame with contacts
            target_company_col: Column name for target company
            personal_research_col: Column name for personal research

        Returns:
            Tuple of:
            - filtered_df: DataFrame with only verified contacts
            - removed_count: Number of contacts removed
            - stats: Dict with verification statistics
        """
        import pandas as pd

        # Add verification columns
        df = df.copy()
        df["employment_verified"] = ""
        df["linkedin_current_company"] = ""
        df["company_match_score"] = 0.0

        verified_count = 0
        mismatch_count = 0
        unknown_count = 0
        removed_indices = []

        for idx, row in df.iterrows():
            target_company = row.get(target_company_col, "")
            personal_research = row.get(personal_research_col, "")

            is_verified, status, current_company, score = self.verify_employment(
                target_company, personal_research
            )

            df.at[idx, "employment_verified"] = status
            df.at[idx, "linkedin_current_company"] = current_company or ""
            df.at[idx, "company_match_score"] = round(score, 2)

            if status == "verified":
                verified_count += 1
            elif status == "mismatch":
                mismatch_count += 1
                removed_indices.append(idx)
            else:  # unknown
                unknown_count += 1

        # Remove mismatched contacts
        filtered_df = df.drop(removed_indices)

        stats = {
            "verified": verified_count,
            "mismatch": mismatch_count,
            "unknown": unknown_count,
            "total_checked": len(df),
            "removed": len(removed_indices)
        }

        return filtered_df, len(removed_indices), stats
