"""
Instantly.ai Email Verification Module
Verifies emails using Instantly.ai API v2

Handles pending status by polling the status endpoint until final result.
"""

import os
import time
import requests
from typing import Dict, List, Tuple
from dotenv import load_dotenv

load_dotenv()

class InstantlyVerifier:
    """Verifies emails using Instantly.ai API"""

    # Configuration for retry logic
    MAX_PENDING_RETRIES = 6  # Max times to check pending status
    PENDING_RETRY_DELAY = 5  # Seconds between pending status checks

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("INSTANTLY_API_KEY")
        if not self.api_key:
            raise ValueError("INSTANTLY_API_KEY not found in environment")

        self.base_url = "https://api.instantly.ai/api/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _map_verification_status(self, verification_status: str) -> str:
        """Map Instantly.ai verification_status to our internal status"""
        status_map = {
            "verified": "verified",
            "valid": "verified",
            "invalid": "unverified",
            "risky": "risky",
            "catch_all": "risky",
            "unknown": "unknown",
            "pending": "pending"  # Keep pending separate so we can retry
        }
        return status_map.get(verification_status.lower(), "unknown")

    def check_verification_status(self, email: str) -> Dict[str, str]:
        """
        Check the verification status of a previously submitted email.
        Uses GET /email-verification/:email endpoint.

        Args:
            email: Email address to check

        Returns:
            Dict with 'email', 'status', and 'result' keys
        """
        url = f"{self.base_url}/email-verification/{email}"

        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            if data.get("status") == "success":
                verification_status = data.get("verification_status", "unknown").lower()
                return {
                    "email": email,
                    "status": self._map_verification_status(verification_status),
                    "result": verification_status
                }
            else:
                return {
                    "email": email,
                    "status": "unknown",
                    "result": f"API Error: {data.get('message', 'Unknown error')}"
                }

        except requests.exceptions.RequestException as e:
            return {
                "email": email,
                "status": "unknown",
                "result": f"Status check failed: {str(e)}"
            }

    def verify_email(self, email: str, retry_pending: bool = True) -> Dict[str, str]:
        """
        Verify a single email using Instantly.ai API.
        If status is 'pending', polls the status endpoint until final result.

        Args:
            email: Email address to verify
            retry_pending: Whether to retry pending emails (default: True)

        Returns:
            Dict with 'email', 'status', and 'result' keys
            status can be: 'verified', 'unverified', 'risky', 'unknown', 'pending'
        """
        url = f"{self.base_url}/email-verification"

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json={"email": email},
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            if data.get("status") == "success":
                verification_status = data.get("verification_status", "unknown").lower()
                mapped_status = self._map_verification_status(verification_status)

                # If pending, poll the status endpoint
                if mapped_status == "pending" and retry_pending:
                    return self._retry_pending_email(email)

                return {
                    "email": email,
                    "status": mapped_status,
                    "result": verification_status
                }
            else:
                return {
                    "email": email,
                    "status": "unknown",
                    "result": f"API Error: {data.get('message', 'Unknown error')}"
                }

        except requests.exceptions.RequestException as e:
            return {
                "email": email,
                "status": "unknown",
                "result": f"Request failed: {str(e)}"
            }

    def _retry_pending_email(self, email: str) -> Dict[str, str]:
        """
        Retry a pending email by polling the status endpoint.

        Args:
            email: Email address to check

        Returns:
            Dict with final verification result
        """
        for attempt in range(1, self.MAX_PENDING_RETRIES + 1):
            time.sleep(self.PENDING_RETRY_DELAY)

            result = self.check_verification_status(email)

            if result["status"] != "pending":
                # Got a final result
                return result

            # Still pending, continue polling

        # Max retries reached, return as unknown (not pending)
        return {
            "email": email,
            "status": "unknown",
            "result": f"pending (timed out after {self.MAX_PENDING_RETRIES} retries)"
        }

    def verify_emails_batch(self, emails: List[str], max_workers: int = 10) -> List[Dict[str, str]]:
        """
        Verify multiple emails IN PARALLEL with progress updates.
        Automatically retries pending emails by polling the status endpoint.

        OPTIMIZED: Uses ThreadPoolExecutor for parallel verification (10x faster!)

        Args:
            emails: List of email addresses to verify
            max_workers: Number of parallel workers (default: 10)

        Returns:
            List of verification results (in same order as input emails)
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        total = len(emails)
        pending_retries = 0

        print(f"\n📧 Starting Instantly.ai verification for {total} emails...")
        print(f"   Using {max_workers} parallel workers (FAST mode)")
        print(f"   Pending emails will be retried up to {self.MAX_PENDING_RETRIES} times\n")

        # Create a dict to store results by email (to preserve order)
        results_map = {}
        completed = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all verification tasks
            future_to_email = {
                executor.submit(self.verify_email, email): email
                for email in emails
            }

            # Process results as they complete
            for future in as_completed(future_to_email):
                email = future_to_email[future]
                try:
                    result = future.result()
                    results_map[email] = result

                    # Check if we had to retry (result contains "timed out")
                    if "pending" in result.get("result", "").lower():
                        pending_retries += 1

                    completed += 1

                    # Show progress every 10 emails or at completion
                    if completed % 10 == 0 or completed == total:
                        status_emoji = {
                            "verified": "✅",
                            "unverified": "❌",
                            "risky": "⚠️",
                            "unknown": "❓",
                            "pending": "⏳"
                        }.get(result["status"], "❓")
                        print(f"   [{completed}/{total}] {status_emoji} {email}: {result['status']}")

                except Exception as e:
                    results_map[email] = {
                        "email": email,
                        "status": "unknown",
                        "result": f"Exception: {str(e)}"
                    }
                    completed += 1

        # Convert results back to list in original order
        results = [results_map.get(email, {"email": email, "status": "unknown", "result": "Not processed"}) for email in emails]

        print(f"\n✅ Verification complete for {total} emails")
        if pending_retries > 0:
            print(f"   ℹ️  {pending_retries} emails required pending retries")
        return results

    def filter_verified_contacts(self, contacts_df, verification_results: List[Dict]) -> Tuple:
        """
        Filter contacts based on email verification status.

        KEEPS: verified, unknown (can't prove they're bad)
        REMOVES: unverified (proven invalid), risky (likely to bounce)

        Args:
            contacts_df: Pandas DataFrame with contact data
            verification_results: List of verification results from verify_emails_batch

        Returns:
            Tuple of (filtered_df, removed_count, verification_stats)
        """
        import pandas as pd

        # Create verification lookup
        verification_map = {r["email"]: r["status"] for r in verification_results}

        # Add verification status column (shows verification status for all contacts)
        contacts_df["instantly_verified"] = contacts_df["real_email"].map(verification_map).fillna("not_checked")

        # Count stats before filtering
        total = len(contacts_df)
        verified_count = (contacts_df["instantly_verified"] == "verified").sum()
        unverified_count = (contacts_df["instantly_verified"] == "unverified").sum()
        risky_count = (contacts_df["instantly_verified"] == "risky").sum()
        unknown_count = (contacts_df["instantly_verified"] == "unknown").sum()
        not_checked_count = (contacts_df["instantly_verified"] == "not_checked").sum()

        stats = {
            "total": total,
            "verified": verified_count,
            "unverified": unverified_count,
            "risky": risky_count,
            "unknown": unknown_count,
            "not_checked": not_checked_count
        }

        # Filter: Keep verified AND unknown (only remove proven bad emails)
        # - verified: confirmed deliverable
        # - unknown: couldn't verify, but not proven invalid (keep them)
        # - not_checked: no email to verify (keep them)
        # - unverified: proven invalid (remove)
        # - risky: likely to bounce (remove)
        statuses_to_keep = ["verified", "unknown", "not_checked"]
        filtered_df = contacts_df[contacts_df["instantly_verified"].isin(statuses_to_keep)].copy()
        removed_count = total - len(filtered_df)

        print(f"\n📊 Verification Summary:")
        print(f"   ✅ Verified: {verified_count} (kept)")
        print(f"   ❓ Unknown: {unknown_count} (kept - not proven invalid)")
        if not_checked_count > 0:
            print(f"   ⬜ Not checked: {not_checked_count} (kept)")
        print(f"   ❌ Unverified: {unverified_count} (removed - invalid)")
        print(f"   ⚠️  Risky: {risky_count} (removed - may bounce)")
        print(f"   🗑️  Total removed: {removed_count} contacts")
        print(f"   ✨ Keeping: {len(filtered_df)} contacts\n")

        return filtered_df, removed_count, stats
