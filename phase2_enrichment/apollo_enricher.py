"""
Apollo email enrichment
Re-uploads contacts to get real email addresses
"""

import requests
from typing import Dict
from config import APOLLO_API_KEY


class ApolloEmailEnricher:
    """Re-uploads contacts to Apollo to get real emails"""

    def __init__(self, api_key: str = APOLLO_API_KEY):
        self.api_key = api_key
        self.base_url = "https://api.apollo.io/v1"
        self.headers = {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
            'X-Api-Key': self.api_key
        }

    def enrich_email(self, first_name: str, last_name: str, company_domain: str) -> Dict:
        """
        Use Apollo's People Enrichment API to get real email
        This spends credits - only use on high-value contacts!

        Returns:
            {"email": str/None, "email_status": str/None, "error": None/str}
        """
        print(f"   📧 Enriching: {first_name} {last_name} @ {company_domain}")

        # Clean company name from domain (defensive: convert to string first in case it's float/numeric)
        company_domain_str = str(company_domain) if company_domain else ""
        company_name = company_domain_str.replace(".com", "").replace(".co", "").replace("www.", "")

        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "organization_name": company_name,
            "domain": company_domain_str  # Use string version
        }

        try:
            response = requests.post(
                f"{self.base_url}/people/match",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                return {
                    "email": None,
                    "email_status": None,
                    "error": f"API error: {response.status_code}"
                }

            data = response.json()
            person = data.get("person", {})

            email = person.get("email")
            email_status = person.get("email_status")

            if email:
                print(f"   ✅ Email found: {email} ({email_status})")
            else:
                print(f"   ⚠️  No email found")

            return {
                "email": email,
                "email_status": email_status,
                "error": None
            }

        except Exception as e:
            return {
                "email": None,
                "email_status": None,
                "error": f"Exception: {str(e)}"
            }
