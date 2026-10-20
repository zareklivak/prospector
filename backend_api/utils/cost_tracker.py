"""
Real-time cost tracking for pipeline operations
"""
from typing import Dict


class CostTracker:
    """Tracks API costs in real-time as pipeline executes"""

    def __init__(self):
        self.costs = {
            "phase1": 0.0,
            "phase2_emails": 0.0,
            "phase2_linkedin": 0.0,
            "phase2_research": 0.0,
            "phase3_messages": 0.0,
            "total": 0.0
        }
        self.counts = {
            "companies": 0,
            "contacts_scraped": 0,
            "emails_enriched": 0,
            "profiles_scraped": 0,
            "companies_researched": 0,
            "messages_generated": 0
        }

    def add_phase1_cost(self, contacts: int):
        """Phase 1 is free"""
        self.counts["contacts_scraped"] += contacts
        # No cost for Phase 1

    def add_phase2_email_cost(self, emails_unlocked: int, cost_per_email: float = 0.01):
        """Add cost for Apollo email enrichment"""
        cost = emails_unlocked * cost_per_email
        self.costs["phase2_emails"] += cost
        self.counts["emails_enriched"] += emails_unlocked
        self._update_total()

    def add_phase2_linkedin_cost(self, profiles_scraped: int, cost_per_profile: float = 0.015):
        """Add cost for LinkedIn profile + posts scraping"""
        cost = profiles_scraped * cost_per_profile
        self.costs["phase2_linkedin"] += cost
        self.counts["profiles_scraped"] += profiles_scraped
        self._update_total()

    def add_phase2_research_cost(self, companies_researched: int, cost_per_company: float = 0.01):
        """Add cost for Perplexity company research"""
        cost = companies_researched * cost_per_company
        self.costs["phase2_research"] += cost
        self.counts["companies_researched"] += companies_researched
        self._update_total()

    def add_phase3_message_cost(self, messages_generated: int, cost_per_contact: float = 0.03):
        """Add cost for message generation (4 messages per contact)"""
        cost = messages_generated * cost_per_contact
        self.costs["phase3_messages"] += cost
        self.counts["messages_generated"] += messages_generated
        self._update_total()

    def _update_total(self):
        """Recalculate total cost"""
        self.costs["total"] = sum([
            self.costs["phase1"],
            self.costs["phase2_emails"],
            self.costs["phase2_linkedin"],
            self.costs["phase2_research"],
            self.costs["phase3_messages"]
        ])

    def get_total_cost(self) -> float:
        """Get total cost so far"""
        return round(self.costs["total"], 2)

    def get_costs_breakdown(self) -> Dict[str, float]:
        """Get detailed cost breakdown"""
        return {k: round(v, 2) for k, v in self.costs.items()}

    def get_counts(self) -> Dict[str, int]:
        """Get operation counts"""
        return self.counts.copy()

    @staticmethod
    def estimate_cost(
        companies: int,
        contacts_per_company: int,
        enrich_emails: bool = True,
        prospect_only: bool = False,
        skip_linkedin: bool = False,
        waterfall_enrichment: bool = False
    ) -> Dict[str, float]:
        """
        Estimate total cost before running pipeline

        Args:
            companies: Number of companies
            contacts_per_company: Contacts per company
            enrich_emails: Whether to enrich emails
            prospect_only: If True, skip Phase 3 and LinkedIn
            skip_linkedin: Skip LinkedIn scraping
            waterfall_enrichment: Use waterfall (more API calls) vs fast mode

        Returns:
            Dictionary with cost breakdown
        """
        total_contacts = companies * contacts_per_company

        # Assume ~60% of contacts will have verified emails after enrichment
        expected_verified = int(total_contacts * 0.6) if enrich_emails else total_contacts

        # Phase 1: Free (Apollo search)
        phase1_cost = 0.0

        # Phase 2 - Email enrichment
        # Fast mode: Apollo ($0.01) + Instantly ($0.01) = $0.02 per contact
        # Waterfall: Up to Apollo + Hunter + Findymail + 3x Instantly = ~$0.06 per contact (worst case)
        if enrich_emails:
            if waterfall_enrichment:
                # Waterfall: average ~$0.03 per contact (most find email on first try)
                phase2_email_cost = total_contacts * 0.03
            else:
                # Fast mode: $0.02 per contact (Apollo + Instantly)
                phase2_email_cost = total_contacts * 0.02
        else:
            phase2_email_cost = 0.0

        # Phase 2 - LinkedIn scraping (only on verified contacts, skip in prospect_only)
        if prospect_only or skip_linkedin:
            phase2_linkedin_cost = 0.0
        else:
            phase2_linkedin_cost = expected_verified * 0.015

        # Phase 2 - Company research (only in full pipeline mode)
        if prospect_only:
            phase2_research_cost = 0.0
        else:
            phase2_research_cost = companies * 0.01

        phase2_total = phase2_email_cost + phase2_linkedin_cost + phase2_research_cost

        # Phase 3 - Message generation (only in full pipeline mode)
        if prospect_only:
            phase3_cost = 0.0
        else:
            phase3_cost = expected_verified * 0.03

        # Total
        total_cost = phase1_cost + phase2_total + phase3_cost

        return {
            "phase1": round(phase1_cost, 2),
            "phase2": round(phase2_total, 2),
            "phase3": round(phase3_cost, 2),
            "total": round(total_cost, 2),
            "per_contact": round(total_cost / total_contacts, 4) if total_contacts > 0 else 0.0
        }
