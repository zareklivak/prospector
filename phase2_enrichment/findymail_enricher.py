"""
Findymail Email Enrichment
Uses Findymail API to find and verify professional emails

API Documentation: https://app.findymail.com/docs/
"""

import os
import requests
from typing import Dict
from dotenv import load_dotenv

load_dotenv()


class FindymailEnricher:
    """Find and verify emails using Findymail API"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("FINDYMAIL_API_KEY")
        if not self.api_key:
            raise ValueError("FINDYMAIL_API_KEY not found in environment")

        self.base_url = "https://app.findymail.com/api"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def enrich_email(self, first_name: str, last_name: str, company_domain: str) -> Dict:
        """
        Use Findymail Email Finder to get professional email.
        Uses one finder credit if a verified email is found.

        Args:
            first_name: Contact's first name
            last_name: Contact's last name
            company_domain: Company domain (e.g., "stripe.com")

        Returns:
            {"email": str/None, "email_status": str/None, "error": None/str}
        """
        print(f"   🔍 Findymail: {first_name} {last_name} @ {company_domain}")

        # Clean domain
        company_domain_str = str(company_domain) if company_domain else ""
        if not company_domain_str:
            return {
                "email": None,
                "email_status": None,
                "error": "No company domain provided"
            }

        # Findymail uses full_name and domain
        full_name = f"{first_name} {last_name}".strip()

        payload = {
            "name": full_name,
            "domain": company_domain_str
        }

        try:
            response = requests.post(
                f"{self.base_url}/search/name",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            data = response.json()

            # Check for specific error codes
            if response.status_code == 402:
                print(f"   ⚠️  Findymail: Not enough credits")
                return {
                    "email": None,
                    "email_status": None,
                    "error": "Not enough credits"
                }

            if response.status_code == 423:
                print(f"   ⚠️  Findymail: Subscription is paused")
                return {
                    "email": None,
                    "email_status": None,
                    "error": "Subscription is paused"
                }

            if response.status_code != 200:
                error_msg = data.get("message", f"API error: {response.status_code}")
                print(f"   ⚠️  Findymail error: {error_msg}")
                return {
                    "email": None,
                    "email_status": None,
                    "error": error_msg
                }

            # Extract email from response
            # Response format: {"email": "john@example.com", "verified": true, "provider": "Google"}
            email = data.get("email")
            verified = data.get("verified", False)
            provider = data.get("provider", "")

            if email:
                email_status = "verified" if verified else "unverified"
                provider_info = f" ({provider})" if provider else ""
                print(f"   ✅ Found: {email}{provider_info} - {email_status}")
            else:
                email_status = None
                print(f"   ⚠️  No email found")

            return {
                "email": email,
                "email_status": email_status,
                "error": None
            }

        except requests.exceptions.RequestException as e:
            return {
                "email": None,
                "email_status": None,
                "error": f"Request failed: {str(e)}"
            }
        except Exception as e:
            return {
                "email": None,
                "email_status": None,
                "error": f"Exception: {str(e)}"
            }

    def verify_email(self, email: str) -> Dict:
        """
        Verify an email using Findymail Email Verifier.
        Uses one verifier credit on all attempted verification.

        Args:
            email: Email address to verify

        Returns:
            {"email": str, "status": str, "result": str, "provider": str}
        """
        if not email:
            return {
                "email": email,
                "status": "unknown",
                "result": "No email provided",
                "provider": ""
            }

        payload = {
            "email": email
        }

        try:
            response = requests.post(
                f"{self.base_url}/verify",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            data = response.json()

            # Check for specific error codes
            if response.status_code == 402:
                return {
                    "email": email,
                    "status": "unknown",
                    "result": "Not enough credits",
                    "provider": ""
                }

            if response.status_code == 423:
                return {
                    "email": email,
                    "status": "unknown",
                    "result": "Subscription is paused",
                    "provider": ""
                }

            if response.status_code != 200:
                return {
                    "email": email,
                    "status": "unknown",
                    "result": f"API error: {response.status_code}",
                    "provider": ""
                }

            # Response: {"email": "john@example.com", "verified": true, "provider": "Google"}
            verified = data.get("verified", False)
            provider = data.get("provider", "")

            status = "verified" if verified else "unverified"

            return {
                "email": email,
                "status": status,
                "result": "valid" if verified else "invalid",
                "provider": provider
            }

        except Exception as e:
            return {
                "email": email,
                "status": "unknown",
                "result": f"Exception: {str(e)}",
                "provider": ""
            }

    def get_credits(self) -> Dict:
        """
        Check remaining Findymail API credits.

        Returns:
            {"finder_credits": int, "verifier_credits": int, "error": None/str}
        """
        try:
            response = requests.get(
                f"{self.base_url}/credits",
                headers=self.headers,
                timeout=30
            )

            data = response.json()

            if response.status_code != 200:
                return {
                    "finder_credits": 0,
                    "verifier_credits": 0,
                    "error": f"API error: {response.status_code}"
                }

            # Extract credit info
            return {
                "finder_credits": data.get("finder_credits", data.get("credits", 0)),
                "verifier_credits": data.get("verifier_credits", data.get("credits", 0)),
                "error": None
            }

        except Exception as e:
            return {
                "finder_credits": 0,
                "verifier_credits": 0,
                "error": str(e)
            }
