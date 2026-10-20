"""
Use Case Matcher
Maps company types to relevant Waypoint use cases for personalization.
Also detects company type from research and intelligently selects use cases
based on person's role and interests.

ENHANCED: Now uses comprehensive use_case_config.py with production (Tier 1)
and adjacent (Tier 2) use cases, plus title-based intelligent selection.
"""

from typing import List, Dict, Tuple, Optional
import random
import re
from use_case_config import get_vertical_config, get_all_vertical_names, VERTICAL_CONFIG


class UseCaseMatcher:
    """Matches company types to relevant operational use cases."""

    # Use case definitions by company type
    USE_CASE_MAP = {
        "broker": {
            "primary": [
                "carrier sales (inbound/outbound)",
                "load booking",
                "POD collection",
                "driver services"
            ],
            "secondary": [
                "payment status updates",
                "shipper sales",
                "in-transit check calls"
            ]
        },
        "carrier": {
            "primary": [
                "driver recruiting",
                "appointment scheduling",
                "inbound sales",
                "customer support"
            ],
            "secondary": [
                "collection calls",
                "breakdown management",
                "capacity sourcing"
            ]
        },
        "3pl": {
            "primary": [
                "appointment scheduling",
                "customer support",
                "track and trace",
                "capacity sourcing"
            ],
            "secondary": [
                "inbound sales",
                "load booking",
                "payment collections"
            ]
        },
        "forwarder": {
            "primary": [
                "cargo coordination",
                "container tracking",
                "delivery confirmation",
                "customer quotation"
            ],
            "secondary": [
                "capacity sourcing",
                "document collection",
                "customs coordination"
            ]
        },
        "shipper": {
            "primary": [
                "dispatch coordination",
                "tracking",
                "escalations",
                "carrier management"
            ],
            "secondary": [
                "appointment scheduling",
                "document management",
                "support"
            ]
        },
        "manufacturer": {
            "primary": [
                "procurement",
                "dispatch",
                "supply chain visibility",
                "vendor coordination"
            ],
            "secondary": [
                "track and trace",
                "quality control comms",
                "logistics support"
            ]
        },
        "ltl carrier": {
            "primary": [
                "driver recruiting",
                "appointment scheduling",
                "customer support",
                "linehaul coordination"
            ],
            "secondary": [
                "inbound sales",
                "collection calls",
                "breakdown management"
            ]
        },
        "ocean carrier": {
            "primary": [
                "container tracking",
                "booking management",
                "vessel scheduling coordination",
                "port operations"
            ],
            "secondary": [
                "document processing",
                "customs coordination",
                "detention management"
            ]
        },
        "air freight": {
            "primary": [
                "cargo sales (RFQ automation, quote and booking)",
                "shipment tracking (AWB)",
                "flight availability search",
                "contact center automation"
            ],
            "secondary": [
                "prioritize inbound requests",
                "customs coordination",
                "capacity management"
            ]
        },
        "commercial airline": {
            "primary": [
                "disruption rebooking",
                "baggage support",
                "contact center automation",
                "passenger services"
            ],
            "secondary": [
                "prioritize inbound requests",
                "flight notifications",
                "loyalty program support"
            ]
        }
    }

    # Company type plural forms for social proof
    COMPANY_TYPE_PLURALS = {
        "broker": "brokers",
        "carrier": "carriers",
        "3pl": "3PLs",
        "forwarder": "forwarders",
        "shipper": "shippers",
        "manufacturer": "manufacturers",
        "ltl carrier": "LTL carriers",
        "ocean carrier": "ocean carriers",
        "air freight": "air freight carriers",
        "commercial airline": "commercial airlines",
        "4pl": "4PLs",
        "retailer": "retailers",
        "distributor": "distributors",
        "warehouse": "warehousing companies",
        "ecommerce": "ecommerce fulfillment companies"
    }

    def __init__(self):
        pass

    def detect_company_type(self, company_research: str, title: str = "", override: Optional[str] = None) -> Tuple[str, str]:
        """
        Detect company type from research and title, with optional manual override.

        Args:
            company_research: Company research text
            title: Person's job title
            override: Manual company type selection (overrides auto-detection)

        Returns:
            (company_type_key, company_type_plural)
        """
        # If manual override provided, use it
        if override:
            override_lower = override.lower().replace("/", "_").replace(" ", "_")
            # Map frontend selections to internal keys
            override_map = {
                "carrier": "carrier",
                "freight_broker": "freight_broker",
                "3pl": "3pl",
                "ocean_carrier": "ocean_carrier",
                "air_freight": "air_freight",
                "food_distributor": "food_distributor",
                "shipper": "shipper",
                "warehousing": "warehousing",
                "customs_broker": "customs_broker"
            }

            for key_variant, canonical_key in override_map.items():
                if key_variant in override_lower:
                    config = get_vertical_config(canonical_key)
                    return (canonical_key, self._get_company_type_plural(canonical_key))

        # Auto-detection logic (existing behavior)
        research_lower = company_research.lower()
        title_lower = title.lower()

        # Check for food distributor
        if "food distributor" in research_lower or "foodservice distributor" in research_lower or ("food" in research_lower and "distribution" in research_lower):
            return ("food_distributor", "food distributors")

        # Check for warehousing/distribution center
        if "warehouse" in research_lower or "warehousing" in research_lower or "distribution center" in research_lower:
            return ("warehousing", "warehousing companies")

        # Check for customs broker
        if "customs broker" in research_lower or "customs brokerage" in research_lower or ("customs" in research_lower and "clearance" in research_lower):
            return ("customs_broker", "customs brokers")

        # Check for ocean carrier
        if "ocean carrier" in research_lower or "shipping company" in research_lower or "container shipping" in research_lower or "shipping line" in research_lower:
            return ("ocean_carrier", "ocean carriers")

        # Check for air freight (cargo airlines)
        if "air freight" in research_lower or "air cargo" in research_lower or "cargo airline" in research_lower or "awb" in research_lower:
            return ("air_freight", "air freight carriers")

        # Check for commercial airline (passenger)
        if "commercial airline" in research_lower or "passenger airline" in research_lower or ("airline" in research_lower and "passenger" in research_lower):
            return ("air_freight", "air freight carriers")  # Map to air_freight vertical

        # Check for airline (generic fallback)
        if "airline" in research_lower:
            return ("air_freight", "air freight carriers")

        # Check for freight broker
        if "freight broker" in research_lower or "brokerage" in research_lower:
            return ("freight_broker", "freight brokers")

        # Check for 3PL/forwarder (merge forwarder into 3PL)
        if "3pl" in research_lower or "third party logistics" in research_lower or "third-party logistics" in research_lower or "freight forwarder" in research_lower or "forwarding" in research_lower:
            return ("3pl", "3PLs")

        # Check for carrier (trucking - includes LTL)
        if "carrier" in research_lower or "trucking" in research_lower or "fleet" in research_lower or "ltl carrier" in research_lower or "less-than-truckload" in research_lower:
            return ("carrier", "carriers")

        # Check for shipper/manufacturer
        if "shipper" in research_lower or "manufacturer" in research_lower or "manufacturing" in research_lower:
            return ("shipper", "shippers")

        # Default based on title if available
        if "linehaul" in title_lower or "fleet" in title_lower:
            return ("carrier", "carriers")

        # Default to carrier (most common)
        return ("carrier", "carriers")

    def _get_company_type_plural(self, company_type: str) -> str:
        """Get plural form of company type for social proof."""
        plurals = {
            "carrier": "carriers",
            "freight_broker": "freight brokers",
            "3pl": "3PLs",
            "ocean_carrier": "ocean carriers",
            "air_freight": "air freight carriers",
            "food_distributor": "food distributors",
            "shipper": "shippers",
            "warehousing": "warehousing companies",
            "customs_broker": "customs brokers"
        }
        return plurals.get(company_type, "companies")

    def detect_role_interests(self, personal_research: str, title: str) -> List[str]:
        """
        Detect what the person is interested in based on their posts and title.
        Returns keywords like ['ai', 'automation', 'scaling', 'visibility', etc.]
        """
        interests = []
        combined = (personal_research + " " + title).lower()

        # AI/Automation interests
        if any(word in combined for word in ['ai', 'artificial intelligence', 'automation', 'rpa', 'machine learning']):
            interests.append('automation')

        # Digital transformation
        if any(word in combined for word in ['digital transformation', 'innovation', 'transformation', 'modernization']):
            interests.append('transformation')

        # Operations/efficiency
        if any(word in combined for word in ['operations', 'efficiency', 'optimization', 'process improvement']):
            interests.append('efficiency')

        # Growth/scaling
        if any(word in combined for word in ['growth', 'scaling', 'expansion', 'headcount']):
            interests.append('scaling')

        # Customer service
        if any(word in combined for word in ['customer service', 'customer experience', 'support']):
            interests.append('customer_service')

        # Visibility/tracking
        if any(word in combined for word in ['visibility', 'tracking', 'transparency', 'real-time']):
            interests.append('visibility')

        return interests

    def get_intelligent_use_cases(
        self,
        company_type: str,
        personal_research: str,
        title: str,
        count: int = 4
    ) -> List[str]:
        """
        Intelligently select use cases based on company type AND person's title/role.

        Strategy:
        - Favor Tier 1 (production) use cases when industry matches exactly
        - Include Tier 2 (adjacent) use cases when title suggests relevance
        - Rank by title keyword matching to prioritize most relevant use cases

        Args:
            company_type: The company type key (e.g., 'carrier', 'freight_broker')
            personal_research: Their LinkedIn research
            title: Their job title
            count: Number of use cases to return (default 3-4)

        Returns:
            List of most relevant use case name strings
        """
        # Get vertical configuration
        vertical = get_vertical_config(company_type)
        all_use_cases = vertical["use_cases"]

        title_lower = title.lower()

        # Score use cases based on title relevance and priority
        scored_cases = []
        for use_case in all_use_cases:
            score = 0

            # Title matching: check if any relevant_titles keywords appear in the person's title
            title_match_count = sum(
                1 for keyword in use_case["relevant_titles"]
                if keyword.lower() in title_lower
            )
            score += title_match_count * 10  # Heavy weight for title matching

            # Priority boost: favor Tier 1 (production) use cases
            if use_case["priority"] == 1:
                score += 5  # Production use cases get significant boost
            else:
                score += 1  # Tier 2 still considered if title matches

            # Add some randomness to avoid always picking same use cases
            score += random.uniform(0, 0.5)

            scored_cases.append((use_case["name"], score))

        # Sort by score (descending) and select top N
        scored_cases.sort(key=lambda x: x[1], reverse=True)
        selected = [name for name, score in scored_cases[:count]]

        # If we didn't get enough (some verticals have fewer use cases), return what we have
        return selected[:count]

    def get_value_props(
        self,
        company_type: str,
        title: str,
        count: int = 3
    ) -> List[str]:
        """
        Intelligently select value propositions based on company type AND person's title/role.

        Strategy:
        - Score each value prop by title keyword matching
        - Add randomness to avoid identical selections
        - Return top-ranked value props

        Args:
            company_type: The company type key
            title: Person's job title (used for title-aware selection)
            count: Number of value props to return (default 3)

        Returns:
            List of value proposition text strings
        """
        vertical = get_vertical_config(company_type)
        value_props = vertical["value_props"]

        title_lower = title.lower()

        # Score value props based on title relevance
        scored_props = []
        for value_prop in value_props:
            score = 0

            # Title matching: check if any relevant_titles keywords appear in the person's title
            title_match_count = sum(
                1 for keyword in value_prop["relevant_titles"]
                if keyword.lower() in title_lower
            )
            score += title_match_count * 10  # Heavy weight for title matching

            # Add some randomness to avoid always picking same value props
            score += random.uniform(0, 2.0)

            scored_props.append((value_prop["text"], score))

        # Sort by score (descending) and select top N
        scored_props.sort(key=lambda x: x[1], reverse=True)
        selected = [text for text, score in scored_props[:count]]

        # If we didn't get enough (some verticals have fewer value props), return what we have
        return selected[:count]

    def format_use_cases_inline(self, use_cases: List[str]) -> str:
        """
        Format use cases for inline mention in a sentence.

        Args:
            use_cases: List of use case strings

        Returns:
            Formatted string like "appointment scheduling, tracking updates, and carrier sourcing"
        """
        if not use_cases:
            return "operational work"

        # Clean up use cases (remove parentheticals for inline)
        cleaned = [re.sub(r'\s*\([^)]*\)', '', uc).strip() for uc in use_cases]

        if len(cleaned) == 1:
            return cleaned[0]
        elif len(cleaned) == 2:
            return f"{cleaned[0]} and {cleaned[1]}"
        else:
            # Join all but last with commas, then add "and" before last
            return f"{', '.join(cleaned[:-1])}, and {cleaned[-1]}"

    def get_social_proof_companies(self, count: int = 3) -> str:
        """
        Get random selection of company names for social proof.

        Args:
            count: Number of companies to select (default 3)

        Returns:
            Comma-separated string like "Northbound Freight, Keystone Logistics, and Harbor Line Carriers"
        """
        companies = ["Northbound Freight", "Keystone Logistics", "Harbor Line Carriers", "Summit Haulage", "Redwood Transport", "Atlas Drayage"]
        selected = random.sample(companies, min(count, len(companies)))

        if len(selected) == 1:
            return selected[0]
        elif len(selected) == 2:
            return f"{selected[0]} and {selected[1]}"
        else:
            return f"{', '.join(selected[:-1])}, and {selected[-1]}"

    def get_social_proof_generic(self) -> str:
        """
        Get random generic social proof statement.

        Returns:
            String like "some of the largest freight brokers"
        """
        options = [
            "some of the largest freight brokers",
            "major ocean and LTL carriers",
            "fast-growing regional carriers"
        ]
        return random.choice(options)
