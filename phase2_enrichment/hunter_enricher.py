"""
Hunter.io Email Enrichment
Uses Hunter.io API to find professional emails

API Documentation: https://hunter.io/api-documentation/v2
"""

import os
import requests
from typing import Dict
from dotenv import load_dotenv

load_dotenv()


class HunterEnricher:
    """Find emails using Hunter.io Email Finder API"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("HUNTER_API_KEY")
        if not self.api_key:
            raise ValueError("HUNTER_API_KEY not found in environment")

        self.base_url = "https://api.hunter.io/v2"

    def enrich_email(self, first_name: str, last_name: str, company_domain: str) -> Dict:
        """
        Use Hunter.io Email Finder to get professional email.

        Args:
            first_name: Contact's first name
            last_name: Contact's last name
            company_domain: Company domain (e.g., "stripe.com")

        Returns:
            {"email": str/None, "email_status": str/None, "confidence": int/None, "error": None/str}
        """
        print(f"   🔍 Hunter.io: {first_name} {last_name} @ {company_domain}")

        # Clean domain
        company_domain_str = str(company_domain) if company_domain else ""
        if not company_domain_str:
            return {
                "email": None,
                "email_status": None,
                "confidence": None,
                "error": "No company domain provided"
            }

        params = {
            "domain": company_domain_str,
            "first_name": first_name,
            "last_name": last_name,
            "api_key": self.api_key
        }

        try:
            response = requests.get(
                f"{self.base_url}/email-finder",
                params=params,
                timeout=30
            )

            data = response.json()

            # Check for errors
            if response.status_code != 200:
                error_msg = data.get("errors", [{}])[0].get("details", f"API error: {response.status_code}")
                print(f"   ⚠️  Hunter error: {error_msg}")
                return {
                    "email": None,
                    "email_status": None,
                    "confidence": None,
                    "error": error_msg
                }

            # Extract email data
            email_data = data.get("data", {})
            email = email_data.get("email")
            confidence = email_data.get("score", 0)  # Hunter returns confidence score 0-100

            if email:
                # Map Hunter confidence to status
                if confidence >= 90:
                    email_status = "verified"
                elif confidence >= 70:
                    email_status = "likely"
                elif confidence >= 50:
                    email_status = "guessed"
                else:
                    email_status = "low_confidence"

                print(f"   ✅ Found: {email} (confidence: {confidence}%)")
            else:
                email_status = None
                print(f"   ⚠️  No email found")

            return {
                "email": email,
                "email_status": email_status,
                "confidence": confidence,
                "error": None
            }

        except requests.exceptions.RequestException as e:
            return {
                "email": None,
                "email_status": None,
                "confidence": None,
                "error": f"Request failed: {str(e)}"
            }
        except Exception as e:
            return {
                "email": None,
                "email_status": None,
                "confidence": None,
                "error": f"Exception: {str(e)}"
            }

    def verify_email(self, email: str) -> Dict:
        """
        Verify an email using Hunter.io Email Verifier.
        Note: We primarily use Instantly.ai for verification, this is a backup.

        Args:
            email: Email address to verify

        Returns:
            {"email": str, "status": str, "result": str}
        """
        if not email:
            return {
                "email": email,
                "status": "unknown",
                "result": "No email provided"
            }

        params = {
            "email": email,
            "api_key": self.api_key
        }

        try:
            response = requests.get(
                f"{self.base_url}/email-verifier",
                params=params,
                timeout=30
            )

            data = response.json()

            if response.status_code != 200:
                return {
                    "email": email,
                    "status": "unknown",
                    "result": f"API error: {response.status_code}"
                }

            email_data = data.get("data", {})
            result = email_data.get("result", "unknown")

            # Map Hunter results to our status format
            # Hunter results: deliverable, undeliverable, risky, unknown
            status_map = {
                "deliverable": "verified",
                "undeliverable": "unverified",
                "risky": "risky",
                "unknown": "unknown"
            }

            status = status_map.get(result, "unknown")

            return {
                "email": email,
                "status": status,
                "result": result
            }

        except Exception as e:
            return {
                "email": email,
                "status": "unknown",
                "result": f"Exception: {str(e)}"
            }

    def get_credits(self) -> Dict:
        """
        Check remaining Hunter.io API credits.

        Returns:
            {"searches": int, "verifications": int, "error": None/str}
        """
        try:
            response = requests.get(
                f"{self.base_url}/account",
                params={"api_key": self.api_key},
                timeout=30
            )

            data = response.json()

            if response.status_code != 200:
                return {
                    "searches": 0,
                    "verifications": 0,
                    "error": f"API error: {response.status_code}"
                }

            account_data = data.get("data", {})
            requests_info = account_data.get("requests", {})

            return {
                "searches": requests_info.get("searches", {}).get("available", 0),
                "verifications": requests_info.get("verifications", {}).get("available", 0),
                "error": None
            }

        except Exception as e:
            return {
                "searches": 0,
                "verifications": 0,
                "error": str(e)
            }
