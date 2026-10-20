"""
Phase 2: Contact Enrichment Orchestrator
Main entry point for enriching Phase 1 contacts

Features:
- 5-step optimized enrichment flow
- Checkpoint/resume support for crash recovery
- Parallel processing with configurable workers
"""

import os
import csv
import time
import pandas as pd
from typing import Optional, Dict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from apify_enricher import ApifyEnricher
from apollo_enricher import ApolloEmailEnricher
from hunter_enricher import HunterEnricher
from findymail_enricher import FindymailEnricher
from company_researcher import CompanyResearcher
from instantly_verifier import InstantlyVerifier
from employment_verifier import EmploymentVerifier
from checkpoint_manager import CheckpointManager
from config import API_DELAY_SECONDS, HUNTER_API_KEY, FINDYMAIL_API_KEY

# Personal email domains that should always be rejected
# These are consumer email providers, not corporate domains
PERSONAL_EMAIL_DOMAINS = {
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
    'aol.com', 'icloud.com', 'mail.com', 'protonmail.com',
    'zoho.com', 'yandex.com', 'live.com', 'msn.com',
    'me.com', 'mac.com', 'inbox.com', 'gmx.com',
}


class Phase2Orchestrator:
    """Main orchestrator for Phase 2 enrichment pipeline"""

    def __init__(self):
        self.apify = ApifyEnricher()
        self.apollo = ApolloEmailEnricher()
        self.researcher = CompanyResearcher()
        self.verifier = InstantlyVerifier()
        self.employment_verifier = EmploymentVerifier()
        self.checkpoint_mgr = CheckpointManager()

        # Initialize waterfall enrichers (lazy - only create when needed)
        self._hunter = None
        self._findymail = None

        # Pause/cancel support
        self._paused = False
        self._cancelled = False
        self._current_job_id = None

    @property
    def hunter(self):
        """Lazy initialization of Hunter enricher"""
        if self._hunter is None:
            if HUNTER_API_KEY:
                self._hunter = HunterEnricher()
            else:
                print("   ⚠️  HUNTER_API_KEY not configured")
        return self._hunter

    @property
    def findymail(self):
        """Lazy initialization of Findymail enricher"""
        if self._findymail is None:
            if FINDYMAIL_API_KEY:
                self._findymail = FindymailEnricher()
            else:
                print("   ⚠️  FINDYMAIL_API_KEY not configured")
        return self._findymail

    def pause(self):
        """Pause the current enrichment job"""
        self._paused = True

    def resume(self):
        """Resume a paused enrichment job"""
        self._paused = False

    def cancel(self):
        """Cancel the current enrichment job"""
        self._cancelled = True

    def is_paused(self) -> bool:
        """Check if job is paused"""
        return self._paused

    def is_cancelled(self) -> bool:
        """Check if job is cancelled"""
        return self._cancelled

    def get_current_job_id(self) -> Optional[str]:
        """Get the current job ID for checkpoint reference"""
        return self._current_job_id

    def is_personal_email(self, email: str) -> bool:
        """
        Check if email is from a personal email provider (gmail, yahoo, etc.)

        These should always be rejected as they're not corporate emails.
        """
        if not email:
            return False
        try:
            domain = email.lower().split("@")[1]
            return domain in PERSONAL_EMAIL_DOMAINS
        except (IndexError, AttributeError):
            return False

    def validate_email_domain(self, email: str, target_domain: str) -> bool:
        """
        Check if email domain matches the target company domain.

        This prevents accepting personal emails (gmail.com, yahoo.com) or
        emails from wrong companies.

        Handles:
        - Exact match: john@company.com matches company.com
        - Subdomain match: john@mail.company.com matches company.com
        - Case insensitive comparison

        Args:
            email: Email address to validate
            target_domain: Expected company domain (e.g., "acme.com")

        Returns:
            True if email domain matches target, False otherwise
        """
        if not email or not target_domain:
            return False

        try:
            # Extract domain from email
            email_domain = email.lower().split("@")[1]
            target = target_domain.lower().strip()

            # Exact match
            if email_domain == target:
                return True

            # Subdomain match (email_domain ends with .target_domain)
            if email_domain.endswith(f".{target}"):
                return True

            return False
        except (IndexError, AttributeError):
            return False

    def calculate_profile_quality(self, profile_data: dict) -> dict:
        """
        Calculate profile quality score based on completeness and engagement

        Returns:
            {
                "quality_score": int (0-10),
                "quality_rating": str ("low", "medium", "high", "excellent"),
                "quality_factors": str (description of what contributed to score)
            }
        """
        profile = profile_data.get("profile", {})
        score = 0
        factors = []

        # About section (0-2 points)
        about = profile.get("about", "")
        if about and len(about) > 50:
            if len(about) > 300:
                score += 2
                factors.append("Detailed about section")
            else:
                score += 1
                factors.append("Basic about section")

        # Work experience (0-2 points)
        experiences = profile.get("experiences", [])
        if experiences:
            if len(experiences) >= 3:
                score += 2
                factors.append(f"{len(experiences)} work experiences")
            else:
                score += 1
                factors.append(f"{len(experiences)} work experience(s)")

        # Education (0-1 point)
        educations = profile.get("educations", [])
        if educations:
            score += 1
            factors.append("Education listed")

        # Skills (0-1 point)
        skills = profile.get("skills", [])
        if skills and len(skills) >= 3:
            score += 1
            factors.append(f"{len(skills)} skills")

        # LinkedIn connections (0-2 points)
        # Handle None values from Apify (use "or 0" to convert None to 0)
        connections = profile.get("connections") or 0
        if connections >= 500:
            score += 2
            factors.append(f"{connections}+ connections (strong network)")
        elif connections >= 100:
            score += 1
            factors.append(f"{connections} connections")

        # Followers (0-1 point)
        # Handle None values from Apify (use "or 0" to convert None to 0)
        followers = profile.get("followers") or 0
        if followers >= 1000:
            score += 1
            factors.append(f"{followers:,} followers (influencer)")

        # Phone number available (0-1 point bonus)
        mobile = profile.get("mobileNumber", "")
        if mobile:
            score += 1
            factors.append("Phone available")

        # Determine rating
        if score >= 8:
            rating = "excellent"
        elif score >= 6:
            rating = "high"
        elif score >= 4:
            rating = "medium"
        else:
            rating = "low"

        return {
            "quality_score": score,
            "quality_rating": rating,
            "quality_factors": ", ".join(factors) if factors else "Limited profile data"
        }

    def synthesize_personal_research(self, posts_data: dict, profile_data: dict) -> str:
        """
        Combine LinkedIn posts and profile into personalized research summary
        Extract ALL available fields from the profile actor
        """
        summary_parts = []

        # The profile actor returns data directly (not nested under "profile" key)
        profile = profile_data.get("profile", {})

        # Basic info
        headline = profile.get("headline", "")
        job_title = profile.get("jobTitle", "")
        company_name = profile.get("companyName", "")
        current_job_duration = profile.get("currentJobDuration", "")

        if headline:
            summary_parts.append(f"**Current Role:** {headline}")

        # About section (if available)
        about = profile.get("about", "")
        if about and len(about) > 10:
            # Don't truncate - use full about section
            summary_parts.append(f"\n**About:** {about}")

        # Current position with duration
        if job_title and company_name:
            duration_text = f" ({current_job_duration})" if current_job_duration else ""
            summary_parts.append(f"\n**Current Position:** {job_title} at {company_name}{duration_text}")

        # Work Experience History
        experiences = profile.get("experiences", [])
        if experiences:
            summary_parts.append(f"\n**Work Experience:**")
            for exp in experiences[:1]:  # Show most recent company
                company_title = exp.get("title", "")
                tenure = exp.get("subtitle", "")

                if company_title:
                    summary_parts.append(f"- {company_title}")
                    if tenure:
                        summary_parts.append(f"  Tenure: {tenure}")

                # Get role breakdown
                sub_components = exp.get("subComponents", [])
                if sub_components:
                    summary_parts.append(f"  Roles:")
                    for role in sub_components[:3]:  # Show top 3 roles
                        role_title = role.get("title", "")
                        role_caption = role.get("caption", "")
                        role_desc = role.get("description", [])

                        if role_title:
                            summary_parts.append(f"  • {role_title}")
                            if role_caption:
                                summary_parts.append(f"    {role_caption}")

                            # Add description if available
                            if role_desc:
                                for desc_item in role_desc[:1]:  # First description only
                                    if isinstance(desc_item, dict):
                                        text = desc_item.get("text", "")
                                        if text:
                                            # Limit description to 200 chars
                                            text_short = text[:200] + "..." if len(text) > 200 else text
                                            summary_parts.append(f"    {text_short}")

        # Top Skills
        top_skills = profile.get("topSkillsByEndorsements", "")
        if top_skills:
            summary_parts.append(f"\n**Top Skills:** {top_skills}")

        # Skills with endorsements
        skills = profile.get("skills", [])
        if skills:
            skill_names = [s.get("title", "") for s in skills[:5]]  # Top 5 skills
            if skill_names:
                summary_parts.append(f"\n**Key Skills:** {', '.join(filter(None, skill_names))}")

        # Education
        educations = profile.get("educations", [])
        if educations:
            edu_list = []
            for edu in educations[:2]:  # Top 2 schools
                school = edu.get("title", "")
                if school:
                    edu_list.append(school)
            if edu_list:
                summary_parts.append(f"\n**Education:** {', '.join(edu_list)}")

        # Connections & Influence
        connections = profile.get("connections", "")
        followers = profile.get("followers", "")
        if connections or followers:
            influence = []
            if connections:
                influence.append(f"{connections:,} connections")
            if followers:
                influence.append(f"{followers:,} followers")
            summary_parts.append(f"\n**LinkedIn Influence:** {', '.join(influence)}")

        # Contact info (phone only - email comes from Apollo)
        mobile = profile.get("mobileNumber", "")
        if mobile:
            summary_parts.append(f"\n**Phone:** {mobile}")

        # Recent posts (if available)
        posts = posts_data.get("posts", [])
        if posts:
            summary_parts.append(f"\n**Recent LinkedIn Activity ({len(posts)} posts):**")
            for i, post in enumerate(posts[:5], 1):  # Show all 5 posts
                # Get post text and metadata
                text = post.get("text", post.get("commentary", ""))
                post_date = post.get("postedDate", post.get("date", ""))
                reactions = post.get("numLikes", post.get("reactions", 0))
                comments = post.get("numComments", post.get("comments", 0))

                if text:
                    # Clean up text but don't truncate - show FULL post
                    full_text = text.replace("\n", " ").strip()

                    # Format with metadata
                    post_header = f"\n{i}. "
                    if post_date:
                        post_header += f"[{post_date}] "

                    summary_parts.append(post_header + full_text)

                    # Add engagement if available
                    if reactions or comments:
                        engagement = []
                        if reactions:
                            engagement.append(f"{reactions} reactions")
                        if comments:
                            engagement.append(f"{comments} comments")
                        summary_parts.append(f"   Engagement: {', '.join(engagement)}")
        elif posts_data.get("error"):
            # Note if no posts were found
            summary_parts.append(f"\n**LinkedIn Posts:** No recent posts found")

        if not summary_parts:
            return "No LinkedIn data available"

        return "\n".join(summary_parts)

    def enrich_email_only(self, row: pd.Series, verify_with_instantly: bool = True) -> dict:
        """
        Enrich a single contact with Apollo email + Instantly verification.
        This is "Fast mode" - Apollo only, no waterfall to Hunter/Findymail.

        Flow:
        1. Get email from Apollo API
        2. Validate domain matches target company
        3. Verify deliverability with Instantly.ai (if enabled)

        Args:
            row: Contact data row
            verify_with_instantly: Whether to verify with Instantly.ai (default: True)

        Returns dict with email fields including instantly_verified status
        """
        result = {
            "real_email": "",
            "real_email_status": "",
            "email_source": "",
            "instantly_verified": "not_verified",
            "enrichment_errors": []
        }

        company_domain = row["company_domain"]
        first_name = row["first_name"]
        last_name = row["last_name"]

        # Step 1: Apollo email enrichment
        email_data = self.apollo.enrich_email(first_name, last_name, company_domain)

        if email_data["error"]:
            result["enrichment_errors"].append(f"Apollo: {email_data['error']}")
            return result

        if not email_data["email"]:
            # No email found
            return result

        email = email_data["email"]

        # Step 2a: Always reject personal emails (gmail, yahoo, etc.)
        if self.is_personal_email(email):
            result["enrichment_errors"].append(f"Apollo: personal email rejected")
            print(f"   ⚠️  Apollo: personal email rejected ({email})")
            return result

        # Step 2b: Check if domain matches
        domain_matches = self.validate_email_domain(email, company_domain)

        if domain_matches:
            # Domain matches → set email and verify
            result["real_email"] = email
            result["real_email_status"] = email_data["email_status"] or ""
            result["email_source"] = "apollo"

            if verify_with_instantly:
                try:
                    verification = self.verifier.verify_email(email)
                    status = verification.get("status", "unknown")
                    result["instantly_verified"] = status

                    if status == "verified":
                        print(f"   ✅ Apollo email verified: {email}")
                    else:
                        print(f"   ⚠️  Apollo email not verified ({status}): {email}")
                except Exception as e:
                    result["enrichment_errors"].append(f"Instantly verification: {str(e)}")
                    result["instantly_verified"] = "unknown"
        else:
            # Domain mismatch (but corporate) → verify first, accept if verified
            email_domain = email.split("@")[1] if "@" in email else "unknown"
            print(f"   ⚠️  Apollo: domain mismatch ({email_domain} != {company_domain}), verifying anyway...")

            if verify_with_instantly:
                try:
                    verification = self.verifier.verify_email(email)
                    status = verification.get("status", "unknown")

                    if status == "verified":
                        result["real_email"] = email
                        result["real_email_status"] = email_data["email_status"] or ""
                        result["email_source"] = "apollo"
                        result["instantly_verified"] = status
                        print(f"   ✅ Apollo email verified (corporate alias accepted): {email}")
                    else:
                        result["enrichment_errors"].append(f"Apollo: domain mismatch, not verified ({email_domain})")
                        print(f"   ⚠️  Apollo: domain mismatch and not verified ({status}): {email}")
                except Exception as e:
                    result["enrichment_errors"].append(f"Instantly verification: {str(e)}")
                    print(f"   ⚠️  Apollo: domain mismatch, verification error: {email}")
            else:
                # No verification enabled, reject mismatched domains in fast mode
                result["enrichment_errors"].append(f"Apollo: domain mismatch ({email_domain})")
                print(f"   ⚠️  Apollo: domain mismatch ({email_domain} != {company_domain})")

        return result

    def enrich_email_waterfall(self, row: pd.Series, verify_with_instantly: bool = True) -> dict:
        """
        Waterfall email enrichment: Apollo -> Hunter -> Findymail

        Tries each provider in order. For each provider:
        1. Get email from provider
        2. Validate email domain matches target company_domain (rejects personal emails like gmail.com)
        3. Verify email deliverability with Instantly.ai (if enabled)
        4. Accept if verified, otherwise try next provider

        Stops on first verified email (if verification enabled) or first valid-domain email found.

        Args:
            row: Contact data row (must include first_name, last_name, company_domain)
            verify_with_instantly: Whether to verify each email with Instantly.ai

        Returns dict with email fields including email_source and enrichment_errors
        """
        result = {
            "real_email": "",
            "real_email_status": "",
            "email_source": "",
            "instantly_verified": "not_verified",
            "enrichment_errors": []
        }

        first_name = row["first_name"]
        last_name = row["last_name"]
        company_domain = row["company_domain"]

        # Track which providers were tried
        providers_tried = []

        # Helper function to verify email with Instantly.ai
        def verify_email(email: str) -> str:
            """Verify email with Instantly.ai, return status"""
            if not email or not verify_with_instantly:
                return "not_verified"
            try:
                verification = self.verifier.verify_email(email)
                return verification.get("status", "unknown")
            except Exception as e:
                result["enrichment_errors"].append(f"Instantly verification: {str(e)}")
                return "unknown"

        # ========================================
        # STEP 1: Try Apollo
        # ========================================
        providers_tried.append("apollo")
        apollo_data = self.apollo.enrich_email(first_name, last_name, company_domain)

        if apollo_data.get("email"):
            email = apollo_data["email"]

            # Always reject personal emails (gmail, yahoo, etc.)
            if self.is_personal_email(email):
                print(f"   ⚠️  Apollo: personal email rejected ({email}), trying Hunter...")
                result["enrichment_errors"].append(f"Apollo: personal email rejected")
            # Domain matches → verify as normal
            elif self.validate_email_domain(email, company_domain):
                result["real_email"] = email
                result["real_email_status"] = apollo_data.get("email_status", "")

                if verify_with_instantly:
                    status = verify_email(email)
                    result["instantly_verified"] = status

                    if status == "verified":
                        result["email_source"] = "apollo"
                        print(f"   ✅ Apollo email verified: {email}")
                        return result
                    else:
                        print(f"   ⚠️  Apollo email not verified ({status}), trying Hunter...")
                else:
                    # No verification, accept Apollo email
                    result["email_source"] = "apollo"
                    return result
            # Domain mismatch but corporate → verify first, accept if verified
            else:
                email_domain = email.split("@")[1] if "@" in email else "unknown"
                print(f"   ⚠️  Apollo: domain mismatch ({email_domain} != {company_domain}), verifying anyway...")
                if verify_with_instantly:
                    status = verify_email(email)
                    if status == "verified":
                        result["real_email"] = email
                        result["real_email_status"] = apollo_data.get("email_status", "")
                        result["email_source"] = "apollo"
                        result["instantly_verified"] = status
                        print(f"   ✅ Apollo email verified (corporate alias accepted): {email}")
                        return result
                    else:
                        print(f"   ⚠️  Apollo email not verified ({status}), trying Hunter...")
                        result["enrichment_errors"].append(f"Apollo: domain mismatch, not verified ({email_domain})")
                else:
                    # No verification enabled, skip mismatched domains
                    print(f"   ⚠️  Apollo: domain mismatch ({email_domain}), trying Hunter...")
                    result["enrichment_errors"].append(f"Apollo: domain mismatch ({email_domain})")
        else:
            if apollo_data.get("error"):
                result["enrichment_errors"].append(f"Apollo: {apollo_data['error']}")
            print(f"   ⚠️  No Apollo email, trying Hunter...")

        # ========================================
        # STEP 2: Try Hunter.io
        # ========================================
        if self.hunter:
            providers_tried.append("hunter")
            hunter_data = self.hunter.enrich_email(first_name, last_name, company_domain)

            if hunter_data.get("email"):
                email = hunter_data["email"]

                # Always reject personal emails (gmail, yahoo, etc.)
                if self.is_personal_email(email):
                    print(f"   ⚠️  Hunter: personal email rejected ({email}), trying Findymail...")
                    result["enrichment_errors"].append(f"Hunter: personal email rejected")
                # Domain matches → verify as normal
                elif self.validate_email_domain(email, company_domain):
                    result["real_email"] = email
                    result["real_email_status"] = hunter_data.get("email_status", "")

                    if verify_with_instantly:
                        status = verify_email(email)
                        result["instantly_verified"] = status

                        if status == "verified":
                            result["email_source"] = "hunter"
                            print(f"   ✅ Hunter email verified: {email}")
                            return result
                        else:
                            print(f"   ⚠️  Hunter email not verified ({status}), trying Findymail...")
                    else:
                        # No verification, accept Hunter email
                        result["email_source"] = "hunter"
                        return result
                # Domain mismatch but corporate → verify first, accept if verified
                else:
                    email_domain = email.split("@")[1] if "@" in email else "unknown"
                    print(f"   ⚠️  Hunter: domain mismatch ({email_domain} != {company_domain}), verifying anyway...")
                    if verify_with_instantly:
                        status = verify_email(email)
                        if status == "verified":
                            result["real_email"] = email
                            result["real_email_status"] = hunter_data.get("email_status", "")
                            result["email_source"] = "hunter"
                            result["instantly_verified"] = status
                            print(f"   ✅ Hunter email verified (corporate alias accepted): {email}")
                            return result
                        else:
                            print(f"   ⚠️  Hunter email not verified ({status}), trying Findymail...")
                            result["enrichment_errors"].append(f"Hunter: domain mismatch, not verified ({email_domain})")
                    else:
                        # No verification enabled, skip mismatched domains
                        print(f"   ⚠️  Hunter: domain mismatch ({email_domain}), trying Findymail...")
                        result["enrichment_errors"].append(f"Hunter: domain mismatch ({email_domain})")
            else:
                if hunter_data.get("error"):
                    result["enrichment_errors"].append(f"Hunter: {hunter_data['error']}")
                print(f"   ⚠️  No Hunter email, trying Findymail...")
        else:
            print(f"   ⚠️  Hunter not configured, trying Findymail...")

        # ========================================
        # STEP 3: Try Findymail
        # ========================================
        if self.findymail:
            providers_tried.append("findymail")
            findymail_data = self.findymail.enrich_email(first_name, last_name, company_domain)

            if findymail_data.get("email"):
                email = findymail_data["email"]

                # Always reject personal emails (gmail, yahoo, etc.)
                if self.is_personal_email(email):
                    print(f"   ⚠️  Findymail: personal email rejected ({email})")
                    result["enrichment_errors"].append(f"Findymail: personal email rejected")
                # Domain matches → verify as normal
                elif self.validate_email_domain(email, company_domain):
                    result["real_email"] = email
                    result["real_email_status"] = findymail_data.get("email_status", "")

                    if verify_with_instantly:
                        status = verify_email(email)
                        result["instantly_verified"] = status

                        if status == "verified":
                            result["email_source"] = "findymail"
                            print(f"   ✅ Findymail email verified: {email}")
                            return result
                        else:
                            print(f"   ⚠️  Findymail email not verified ({status})")
                    else:
                        # No verification, accept Findymail email
                        result["email_source"] = "findymail"
                        return result
                # Domain mismatch but corporate → verify first, accept if verified
                else:
                    email_domain = email.split("@")[1] if "@" in email else "unknown"
                    print(f"   ⚠️  Findymail: domain mismatch ({email_domain} != {company_domain}), verifying anyway...")
                    if verify_with_instantly:
                        status = verify_email(email)
                        if status == "verified":
                            result["real_email"] = email
                            result["real_email_status"] = findymail_data.get("email_status", "")
                            result["email_source"] = "findymail"
                            result["instantly_verified"] = status
                            print(f"   ✅ Findymail email verified (corporate alias accepted): {email}")
                            return result
                        else:
                            print(f"   ⚠️  Findymail email not verified ({status})")
                            result["enrichment_errors"].append(f"Findymail: domain mismatch, not verified ({email_domain})")
                    else:
                        # No verification enabled, skip mismatched domains
                        print(f"   ⚠️  Findymail: domain mismatch ({email_domain})")
                        result["enrichment_errors"].append(f"Findymail: domain mismatch ({email_domain})")
            else:
                if findymail_data.get("error"):
                    result["enrichment_errors"].append(f"Findymail: {findymail_data['error']}")
        else:
            print(f"   ⚠️  Findymail not configured")

        # ========================================
        # All providers failed
        # ========================================
        # Only keep emails that passed domain validation (stored in result["real_email"])
        if result["real_email"]:
            print(f"   ⚠️  No verified email found, keeping best: {result['real_email']} ({result['instantly_verified']})")
        else:
            print(f"   ❌ No valid email found from any provider (tried: {', '.join(providers_tried)})")

        return result

    def enrich_linkedin_only(self, row: pd.Series) -> dict:
        """
        Enrich a single contact with LinkedIn data ONLY (no company research).
        This runs on all verified contacts before profile quality filtering.

        OPTIMIZED: Runs profile and posts scraping in PARALLEL to cut time in half.

        Returns dict with LinkedIn fields (profile, posts, quality score)
        """
        result = {
            "linkedin_phone": "",
            "personal_research": "",
            "profile_quality_score": 0,
            "profile_quality_rating": "",
            "profile_quality_factors": "",
            "linkedin_still_employed": None,  # True/False/None from LinkedIn jobStillWorking field
            "enrichment_errors": []
        }

        linkedin_url = row.get("linkedin_url", "")

        # Run profile and posts scraping IN PARALLEL (2x faster)
        profile_data = {"profile": {}, "error": None}
        posts_data = {"posts": [], "error": None}

        with ThreadPoolExecutor(max_workers=2) as executor:
            profile_future = executor.submit(self.apify.scrape_linkedin_profile, linkedin_url)
            posts_future = executor.submit(self.apify.scrape_linkedin_posts, linkedin_url)

            # Wait for both to complete
            profile_data = profile_future.result()
            posts_data = posts_future.result()

        # Process profile data
        if profile_data["error"]:
            result["enrichment_errors"].append(f"Profile: {profile_data['error']}")
        else:
            # Extract phone from LinkedIn profile
            profile = profile_data.get("profile", {})
            linkedin_phone = profile.get("mobileNumber", "")
            if linkedin_phone:
                result["linkedin_phone"] = linkedin_phone

            # Extract jobStillWorking for employment verification
            # This indicates if the person is currently employed at their listed position
            job_still_working = profile.get("jobStillWorking")
            result["linkedin_still_employed"] = job_still_working

        # Process posts data
        if posts_data["error"]:
            result["enrichment_errors"].append(f"Posts: {posts_data['error']}")

        # Calculate profile quality score
        quality_info = self.calculate_profile_quality(profile_data)
        result["profile_quality_score"] = quality_info["quality_score"]
        result["profile_quality_rating"] = quality_info["quality_rating"]
        result["profile_quality_factors"] = quality_info["quality_factors"]

        # Synthesize personal research
        result["personal_research"] = self.synthesize_personal_research(posts_data, profile_data)

        return result

    def enrich_company_research(self, row: pd.Series) -> str:
        """
        Get company research for a single contact.
        This runs AFTER profile quality filtering to avoid wasted API calls.
        Results are cached per company domain.

        Returns company research string
        """
        return self.researcher.research_company(
            row["company_name"],
            row["company_domain"]
        )

    def enrich_linkedin_and_research(self, row: pd.Series) -> dict:
        """
        Enrich a single contact with LinkedIn data and company research.
        LEGACY method - kept for backward compatibility with sequential mode.

        Returns dict with LinkedIn and research fields
        """
        # Get LinkedIn data
        result = self.enrich_linkedin_only(row)

        # Add company research
        result["company_research"] = self.enrich_company_research(row)

        return result

    def enrich_contact(self, row: pd.Series, enrich_email: bool = True) -> dict:
        """
        Enrich a single contact with all Phase 2 data.
        LEGACY method - kept for backward compatibility with sequential mode.

        Returns dict with enriched fields
        """
        result = {
            "real_email": row.get("email", ""),
            "real_email_status": row.get("email_status", ""),
            "linkedin_phone": "",
            "personal_research": "",
            "company_research": "",
            "profile_quality_score": 0,
            "profile_quality_rating": "",
            "profile_quality_factors": "",
            "enrichment_errors": []
        }

        # Email enrichment (if enabled)
        if enrich_email:
            email_result = self.enrich_email_only(row)
            result["real_email"] = email_result["real_email"]
            result["real_email_status"] = email_result["real_email_status"]
            result["enrichment_errors"].extend(email_result["enrichment_errors"])

        # LinkedIn and research enrichment
        linkedin_result = self.enrich_linkedin_and_research(row)
        result["linkedin_phone"] = linkedin_result["linkedin_phone"]
        result["personal_research"] = linkedin_result["personal_research"]
        result["company_research"] = linkedin_result["company_research"]
        result["profile_quality_score"] = linkedin_result["profile_quality_score"]
        result["profile_quality_rating"] = linkedin_result["profile_quality_rating"]
        result["profile_quality_factors"] = linkedin_result["profile_quality_factors"]
        result["enrichment_errors"].extend(linkedin_result["enrichment_errors"])

        return result

    def enrich_contacts_batch(
        self,
        input_csv: str,
        enrich_emails: bool = False,
        max_contacts: Optional[int] = None,
        min_score: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Enrich a batch of contacts from Phase 1 CSV

        Args:
            input_csv: Path to Phase 1 CSV file
            enrich_emails: Whether to spend Apollo credits on email enrichment
            max_contacts: Limit number of contacts to enrich (for testing)
            min_score: Only enrich contacts with score >= this value

        Returns:
            DataFrame with enriched contacts
        """
        print(f"\n{'#'*60}")
        print(f"🚀 PHASE 2: Contact Enrichment")
        print(f"{'#'*60}\n")

        # Load Phase 1 data
        df = pd.read_csv(input_csv)
        print(f"📂 Loaded {len(df)} contacts from Phase 1")

        # Filter by score if specified
        if min_score:
            df = df[df['fit_score'] >= min_score].copy()
            print(f"🎯 Filtered to {len(df)} contacts with score >= {min_score}")

        # Limit contacts if specified
        if max_contacts:
            df = df.head(max_contacts).copy()
            print(f"⚡ Limited to {max_contacts} contacts for processing")

        print(f"\n⚙️  Settings:")
        print(f"   Email enrichment: {'Yes (spending credits)' if enrich_emails else 'No'}")
        print(f"   Total to enrich: {len(df)}")
        print()

        # Add new columns
        df["real_email"] = ""
        df["real_email_status"] = ""
        df["linkedin_phone"] = ""
        df["profile_quality_score"] = 0
        df["profile_quality_rating"] = ""
        df["profile_quality_factors"] = ""
        df["linkedin_still_employed"] = None
        df["personal_research"] = ""
        df["company_research"] = ""
        df["enrichment_errors"] = ""

        # Process each contact
        for idx, row in df.iterrows():
            try:
                enrichment = self.enrich_contact(row, enrich_email=enrich_emails)

                df.at[idx, "real_email"] = enrichment["real_email"] or ""
                df.at[idx, "real_email_status"] = enrichment["real_email_status"] or ""
                df.at[idx, "linkedin_phone"] = enrichment["linkedin_phone"] or ""
                df.at[idx, "profile_quality_score"] = enrichment["profile_quality_score"]
                df.at[idx, "profile_quality_rating"] = enrichment["profile_quality_rating"]
                df.at[idx, "profile_quality_factors"] = enrichment["profile_quality_factors"]
                df.at[idx, "personal_research"] = enrichment["personal_research"]
                df.at[idx, "company_research"] = enrichment["company_research"]
                df.at[idx, "enrichment_errors"] = "; ".join(enrichment["enrichment_errors"])

                print(f"\n✅ Completed {idx+1}/{len(df)}")

                # Rate limiting - be nice to APIs
                if idx < len(df) - 1:  # Don't delay after last contact
                    time.sleep(API_DELAY_SECONDS)

            except Exception as e:
                try:
                    print(f"\n❌ Error enriching contact {idx+1}: {str(e)}")
                except (ValueError, IOError):
                    pass  # Suppress I/O errors when stdout is closed
                df.at[idx, "enrichment_errors"] = str(e)

        print(f"\n{'='*60}")
        print(f"✅ PHASE 2 COMPLETE")
        print(f"{'='*60}")
        print(f"📊 Total enriched: {len(df)}")
        print()

        return df

    def enrich_contacts_batch_parallel(
        self,
        input_csv: str,
        enrich_emails: bool = False,
        waterfall_enrichment: bool = False,
        verify_current_employment: bool = False,
        skip_linkedin: bool = False,
        skip_company_research: bool = False,
        max_contacts: Optional[int] = None,
        min_score: Optional[int] = None,
        min_profile_quality: Optional[int] = None,
        max_workers: int = 12,
        resume_from_checkpoint: bool = True,
        checkpoint_interval: int = 10
    ) -> pd.DataFrame:
        """
        Enrich a batch of contacts using parallel processing (FASTER!)

        FULLY OPTIMIZED FLOW (filters early to save API costs):
        1. Email enrichment via waterfall (Apollo -> Hunter -> Findymail with Instantly verification)
        2. LinkedIn scraping (Apify) - expensive, only on verified contacts (SKIPPED if skip_linkedin=True)
        2b. Employment verification - verify contacts still work at target company (SKIPPED if skip_linkedin=True)
        3. Profile quality filter - removes low-quality profiles (SKIPPED if skip_linkedin=True)
        4. Company research (Perplexity) - only for remaining contacts, cached per company (SKIPPED if skip_company_research=True)

        Args:
            input_csv: Path to Phase 1 CSV file
            enrich_emails: Whether to enrich emails with Apollo + Instantly verification
            waterfall_enrichment: Use waterfall (Apollo -> Hunter -> Findymail). False = Fast mode (Apollo only)
            verify_current_employment: Whether to verify contacts still work at target company
            skip_linkedin: Skip LinkedIn scraping (saves Apify credits, messages from company research only)
            skip_company_research: Skip company research (for email-only enrichment mode)
            max_contacts: Limit number of contacts to enrich (for testing)
            min_score: Only enrich contacts with fit_score >= this value
            min_profile_quality: Only keep contacts with profile_quality_score >= this value
            max_workers: Number of parallel workers (default: 12, safe for most Apify plans)
            resume_from_checkpoint: Whether to check for and resume from existing checkpoint
            checkpoint_interval: Save checkpoint every N contacts during LinkedIn scraping

        Returns:
            DataFrame with enriched contacts
        """
        # Reset state
        self._paused = False
        self._cancelled = False

        # Build config for checkpoint identification
        config = {
            "enrich_emails": enrich_emails,
            "waterfall_enrichment": waterfall_enrichment,
            "verify_current_employment": verify_current_employment,
            "skip_linkedin": skip_linkedin,
            "skip_company_research": skip_company_research,
            "min_score": min_score,
            "min_profile_quality": min_profile_quality,
            "max_contacts": max_contacts
        }

        # Check for existing checkpoint
        checkpoint = None
        start_step = 1
        # Note: Email verification is now always built into the waterfall enrichment step
        step_status = {
            "email_enrichment": "pending" if enrich_emails else "skipped",
            "linkedin_scraping": "skipped" if skip_linkedin else "pending",
            "employment_verification": "skipped" if (skip_linkedin or not verify_current_employment) else "pending",
            "profile_quality_filter": "skipped" if (skip_linkedin or not min_profile_quality or min_profile_quality <= 1) else "pending",
            "company_research": "skipped" if skip_company_research else "pending"
        }

        if resume_from_checkpoint:
            checkpoint = self.checkpoint_mgr.find_checkpoint(input_csv, config)
            if checkpoint:
                print(f"\n{'='*60}")
                print(f"📂 RESUMING FROM CHECKPOINT")
                print(f"{'='*60}")
                print(f"   Job ID: {checkpoint['job_id']}")
                print(f"   Last updated: {checkpoint['updated_at']}")
                print(f"   Current step: {self.checkpoint_mgr.get_step_name(checkpoint['current_step'])}")
                print(f"   Contacts: {checkpoint['total_contacts']}")
                print()

                # Load checkpoint data
                df = self.checkpoint_mgr.load_checkpoint_data(checkpoint)
                start_step = checkpoint["current_step"]
                step_status = checkpoint["step_status"]
                self._current_job_id = checkpoint["job_id"]

                # Update step_status for new features that might not exist in old checkpoints
                # or that have different settings in the current run config
                if "employment_verification" not in step_status:
                    step_status["employment_verification"] = "pending" if verify_current_employment else "skipped"
                elif verify_current_employment and step_status.get("employment_verification") == "skipped":
                    # User now wants employment verification but checkpoint had it skipped
                    step_status["employment_verification"] = "pending"

                # Jump to the appropriate step based on checkpoint
                print(f"   Resuming from Step {start_step}...")
                print()

        if not checkpoint:
            print(f"\n🚀 PHASE 2: Contact Enrichment (Fully Optimized Flow)")

            # Load Phase 1 data
            df = pd.read_csv(input_csv)
            print(f"📂 Loaded {len(df)} contacts from Phase 1")

            # Filter by score if specified
            if min_score:
                df = df[df['fit_score'] >= min_score].copy()
                print(f"🎯 Filtering to {len(df)} high-quality contacts (score >= {min_score})")

            # Limit contacts if specified
            if max_contacts:
                df = df.head(max_contacts).copy()
                print(f"⚡ Limited to {max_contacts} contacts for processing")

            print(f"\n📋 Processing {len(df)} contacts...")
            print()

            # Add new columns
            df["real_email"] = ""
            df["real_email_status"] = ""
            df["email_source"] = ""  # Tracks which provider found the email (apollo/hunter/findymail)
            df["linkedin_phone"] = ""
            df["profile_quality_score"] = 0
            df["profile_quality_rating"] = ""
            df["profile_quality_factors"] = ""
            df["linkedin_still_employed"] = None
            df["personal_research"] = ""
            df["company_research"] = ""
            df["enrichment_errors"] = ""
            df["instantly_verified"] = "not_verified"
            df["employment_verified"] = ""
            df["linkedin_current_company"] = ""
            df["company_match_score"] = 0.0

            # Create initial checkpoint
            self._current_job_id = self.checkpoint_mgr.create_checkpoint(
                input_csv=input_csv,
                config=config,
                df=df,
                current_step=1,
                step_status=step_status
            )
            print(f"💾 Checkpoint created: {self._current_job_id}")
            print()

        original_count = len(df)

        # ============================================================
        # STEP 1: Email Enrichment (Apollo or Waterfall)
        # ============================================================
        if (enrich_emails or waterfall_enrichment) and start_step <= 1 and step_status.get("email_enrichment") != "complete":
            if waterfall_enrichment:
                print(f"{'='*60}")
                print(f"🌊 STEP 1: Waterfall Email Enrichment (Apollo -> Hunter -> Findymail)")
                print(f"{'='*60}")
                print(f"   Processing {len(df)} contacts with waterfall + verification...")
                print(f"   Note: Verification is built into waterfall - will stop on first verified email")
                print()
            else:
                print(f"{'='*60}")
                print(f"📧 STEP 1: Email Enrichment (Apollo)")
                print(f"{'='*60}")
                print(f"   Processing {len(df)} contacts...")

            step_status["email_enrichment"] = "in_progress"
            completed = 0
            stats = {"verified": 0, "invalid": 0, "no_email": 0, "domain_mismatch": 0, "error": 0}
            total_contacts = len(df)

            # Choose enrichment method based on waterfall setting
            if waterfall_enrichment:
                # Waterfall: Apollo -> Hunter -> Findymail (with built-in verification)
                enrich_func = lambda row: self.enrich_email_waterfall(row, verify_with_instantly=True)
            else:
                # Fast mode: Apollo only (with built-in verification)
                enrich_func = lambda row: self.enrich_email_only(row, verify_with_instantly=True)

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_idx = {
                    executor.submit(enrich_func, row): idx
                    for idx, row in df.iterrows()
                }

                for future in as_completed(future_to_idx):
                    # Check for pause/cancel
                    if self._cancelled:
                        print(f"\n   ⚠️ Cancelled - saving checkpoint...")
                        self.checkpoint_mgr.update_checkpoint(self._current_job_id, df, 1, step_status)
                        raise InterruptedError("Job cancelled by user")

                    idx = future_to_idx[future]
                    try:
                        result = future.result()
                        df.at[idx, "real_email"] = result.get("real_email", "") or ""
                        df.at[idx, "real_email_status"] = result.get("real_email_status", "") or ""
                        # Waterfall adds these fields
                        if "email_source" in result:
                            df.at[idx, "email_source"] = result.get("email_source", "") or ""
                        if "instantly_verified" in result:
                            df.at[idx, "instantly_verified"] = result.get("instantly_verified", "not_verified")
                        if result.get("enrichment_errors"):
                            df.at[idx, "enrichment_errors"] = "; ".join(result["enrichment_errors"])

                        # Track stats for better progress reporting
                        verification_status = result.get("instantly_verified", "not_verified")
                        errors = result.get("enrichment_errors", [])
                        if verification_status == "verified":
                            stats["verified"] += 1
                        elif any("domain mismatch" in str(e).lower() for e in errors):
                            stats["domain_mismatch"] += 1
                        elif not result.get("real_email"):
                            stats["no_email"] += 1
                        else:
                            stats["invalid"] += 1

                        completed += 1
                        # Show progress every 25 contacts or at completion
                        if completed % 25 == 0 or completed == total_contacts:
                            try:
                                pct = int(completed / total_contacts * 100)
                                print(f"   [{pct:3d}%] {completed}/{total_contacts} processed | ✓ {stats['verified']} verified | ✗ {stats['invalid']+stats['no_email']+stats['domain_mismatch']} filtered")
                            except (ValueError, IOError):
                                pass
                    except Exception as e:
                        df.at[idx, "enrichment_errors"] = str(e)
                        stats["error"] += 1
                        completed += 1

            # Show detailed summary
            emails_found = len(df[df['real_email'].notna() & (df['real_email'] != '')])
            verified_count = len(df[df['instantly_verified'] == 'verified'])
            filtered_count = total_contacts - verified_count

            print(f"\n   {'='*50}")
            print(f"   📊 ENRICHMENT SUMMARY")
            print(f"   {'='*50}")
            print(f"   Started with:        {total_contacts} contacts")
            print(f"   ✓ Verified emails:   {verified_count} ({int(verified_count/total_contacts*100) if total_contacts > 0 else 0}%)")
            print(f"   ✗ Filtered out:      {filtered_count} contacts")
            if filtered_count > 0:
                print(f"      - No email found:    {stats['no_email']}")
                print(f"      - Failed verification: {stats['invalid']}")
                print(f"      - Domain mismatch:   {stats['domain_mismatch']}")
                if stats['error'] > 0:
                    print(f"      - Errors:            {stats['error']}")

            if waterfall_enrichment:
                # Count by source for waterfall mode
                apollo_count = len(df[df['email_source'] == 'apollo'])
                hunter_count = len(df[df['email_source'] == 'hunter'])
                findymail_count = len(df[df['email_source'] == 'findymail'])
                print(f"   Source breakdown: Apollo={apollo_count}, Hunter={hunter_count}, Findymail={findymail_count}")

            # Filter to verified only (same for both modes)
            if verified_count > 0:
                df = df[df['instantly_verified'] == 'verified'].copy()
                print(f"\n   ✅ Keeping {len(df)} contacts with verified emails")
            else:
                print(f"\n   ⚠️  No verified emails found - output will be empty")
            print()

            # Mark step complete and save checkpoint
            step_status["email_enrichment"] = "complete"
            self.checkpoint_mgr.update_checkpoint(self._current_job_id, df, 2, step_status)
            print(f"   💾 Checkpoint saved after email enrichment")
            print()

        count_after_email = len(df)

        # ============================================================
        # STEP 2: LinkedIn Scraping (Apify) - Profiles & Posts Only
        # Note: Email verification is now built into the waterfall enrichment step
        # ============================================================
        if step_status.get("linkedin_scraping") == "skipped":
            print(f"{'='*60}")
            print(f"⏭️  STEP 3: LinkedIn Enrichment (SKIPPED)")
            print(f"{'='*60}")
            print(f"   LinkedIn scraping disabled - using company research only")
            print(f"   Contacts: {len(df)}")
            print()

            # Initialize default values for LinkedIn-related columns
            df['linkedin_phone'] = ""
            df['profile_quality_score'] = 0
            df['profile_quality_rating'] = "unknown"
            df['profile_quality_factors'] = "LinkedIn scraping skipped"
            df['personal_research'] = ""
            df['linkedin_still_employed'] = None

        elif start_step <= 3 and step_status.get("linkedin_scraping") != "complete":
            print(f"{'='*60}")
            print(f"🔍 STEP 3: LinkedIn Enrichment (Apify)")
            print(f"{'='*60}")

            step_status["linkedin_scraping"] = "in_progress"

            # Identify contacts that still need LinkedIn enrichment
            # (For resume: skip contacts that already have personal_research)
            contacts_to_process = df[
                (df['personal_research'].isna()) | (df['personal_research'] == '')
            ].copy()

            if len(contacts_to_process) < len(df):
                print(f"   Resuming: {len(df) - len(contacts_to_process)} already processed, {len(contacts_to_process)} remaining")
            else:
                print(f"   Processing {len(df)} contacts...")
            print()

            completed = 0
            total_to_process = len(contacts_to_process)

            if total_to_process > 0:
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    future_to_idx = {
                        executor.submit(self.enrich_linkedin_only, row): idx
                        for idx, row in contacts_to_process.iterrows()
                    }

                    for future in as_completed(future_to_idx):
                        # Check for pause/cancel
                        if self._cancelled:
                            print(f"\n   ⚠️ Cancelled - saving checkpoint...")
                            self.checkpoint_mgr.update_checkpoint(self._current_job_id, df, 3, step_status)
                            raise InterruptedError("Job cancelled by user")

                        if self._paused:
                            print(f"\n   ⏸️ Paused - saving checkpoint...")
                            self.checkpoint_mgr.update_checkpoint(self._current_job_id, df, 3, step_status)
                            # Wait for resume
                            while self._paused and not self._cancelled:
                                time.sleep(1)
                            if self._cancelled:
                                raise InterruptedError("Job cancelled by user")
                            print(f"   ▶️ Resumed...")

                        idx = future_to_idx[future]
                        try:
                            result = future.result()
                            df.at[idx, "linkedin_phone"] = result["linkedin_phone"] or ""
                            df.at[idx, "profile_quality_score"] = result["profile_quality_score"]
                            df.at[idx, "profile_quality_rating"] = result["profile_quality_rating"]
                            df.at[idx, "profile_quality_factors"] = result["profile_quality_factors"]
                            df.at[idx, "personal_research"] = result["personal_research"]
                            df.at[idx, "linkedin_still_employed"] = result["linkedin_still_employed"]

                            # Append LinkedIn errors to existing errors
                            existing_errors = df.at[idx, "enrichment_errors"] or ""
                            if result["enrichment_errors"]:
                                new_errors = "; ".join(result["enrichment_errors"])
                                df.at[idx, "enrichment_errors"] = f"{existing_errors}; {new_errors}" if existing_errors else new_errors

                            completed += 1

                            # Incremental checkpoint every N contacts
                            if completed % checkpoint_interval == 0:
                                self.checkpoint_mgr.update_checkpoint(self._current_job_id, df, 3, step_status)
                                try:
                                    print(f"   💾 Checkpoint saved ({completed}/{total_to_process})")
                                except (ValueError, IOError):
                                    pass

                            if completed % 5 == 0 or completed == total_to_process:
                                try:
                                    print(f"   ✅ Enriched {completed}/{total_to_process} LinkedIn profiles...")
                                except (ValueError, IOError):
                                    pass
                        except Exception as e:
                            existing_errors = df.at[idx, "enrichment_errors"] or ""
                            df.at[idx, "enrichment_errors"] = f"{existing_errors}; LinkedIn: {str(e)}" if existing_errors else f"LinkedIn: {str(e)}"
                            completed += 1

            # Show quality distribution
            try:
                quality_counts = df['profile_quality_rating'].value_counts()
                print(f"\n   📊 Profile quality distribution:")
                for rating in ['excellent', 'high', 'medium', 'low']:
                    count = quality_counts.get(rating, 0)
                    if count > 0:
                        print(f"      {rating}: {count}")
                print()
            except (ValueError, IOError):
                pass

            # Mark step complete and save checkpoint
            step_status["linkedin_scraping"] = "complete"
            self.checkpoint_mgr.update_checkpoint(self._current_job_id, df, 4, step_status)
            print(f"   💾 Checkpoint saved after LinkedIn enrichment")
            print()

        count_after_linkedin = len(df)

        # ============================================================
        # STEP 3b: Employment Verification (Optional)
        # ============================================================
        if step_status.get("employment_verification") == "skipped":
            # Employment verification skipped (either skip_linkedin=True or verify_current_employment=False)
            pass
        elif verify_current_employment and step_status.get("employment_verification") != "complete":
            print(f"{'='*60}")
            print(f"🔍 STEP 3b: Employment Verification")
            print(f"{'='*60}")
            print(f"   Verifying contacts are still employed at target companies...")
            print()

            step_status["employment_verification"] = "in_progress"

            before_filter = len(df)
            df, removed_count, stats = self.employment_verifier.filter_verified_contacts(
                df,
                target_company_col="company_name",
                personal_research_col="personal_research"
            )

            print(f"   📊 Employment verification results:")
            print(f"      ✅ Verified: {stats['verified']} contacts")
            print(f"      ❌ Mismatch: {stats['mismatch']} contacts (different company - removed)")
            print(f"      ⏱️  Not Current: {stats.get('not_current', 0)} contacts (left role - removed)")
            print(f"      ❓ Unknown: {stats['unknown']} contacts (kept)")
            print()

            if removed_count > 0:
                # Calculate savings from skipping downstream processing
                apify_savings = 0  # Already spent on LinkedIn
                perplexity_cost = 0.01  # Rough estimate per company
                savings = removed_count * perplexity_cost
                print(f"   🗑️  Removed {removed_count} contacts no longer at target company")
                print(f"   💵 Estimated Perplexity savings: ${savings:.2f}")
                print()
            else:
                print(f"   ✅ All {len(df)} contacts verified at target companies")
                print()

            # Mark step complete and save checkpoint
            step_status["employment_verification"] = "complete"
            self.checkpoint_mgr.update_checkpoint(self._current_job_id, df, 4, step_status)
            print(f"   💾 Checkpoint saved after employment verification")
            print()

        count_after_employment = len(df)

        # ============================================================
        # STEP 4: Profile Quality Filter (Optional)
        # ============================================================
        if step_status.get("profile_quality_filter") == "skipped":
            # Profile quality filter skipped (either skip_linkedin=True or min_profile_quality <= 1)
            pass
        elif min_profile_quality and min_profile_quality > 1 and start_step <= 4 and step_status.get("profile_quality_filter") != "complete":
            print(f"{'='*60}")
            print(f"🎯 STEP 4: Profile Quality Filter")
            print(f"{'='*60}")

            step_status["profile_quality_filter"] = "in_progress"

            before_filter = len(df)
            df = df[df['profile_quality_score'] >= min_profile_quality].copy()
            removed_count = before_filter - len(df)

            if removed_count > 0:
                # Calculate savings from skipping company research
                perplexity_cost = 0.01  # Rough estimate per company
                unique_companies_removed = removed_count  # Approximate - some may share companies
                savings = unique_companies_removed * perplexity_cost

                print(f"   📊 Keeping {len(df)} contacts (profile_quality >= {min_profile_quality})")
                print(f"   🗑️  Removed {removed_count} low-quality profiles")
                print(f"   💵 Estimated Perplexity savings: ${savings:.2f}")
                print()
            else:
                print(f"   ✅ All {len(df)} contacts meet quality threshold")
                print()

            # Mark step complete and save checkpoint
            step_status["profile_quality_filter"] = "complete"
            self.checkpoint_mgr.update_checkpoint(self._current_job_id, df, 5, step_status)
            print(f"   💾 Checkpoint saved after profile quality filter")
            print()

        # ============================================================
        # STEP 5: Company Research (Perplexity) - ONE call per company
        # SKIPPED if skip_company_research=True (for email-only enrichment)
        # ============================================================
        if len(df) > 0 and start_step <= 5 and step_status.get("company_research") not in ("complete", "skipped"):
            print(f"{'='*60}")
            print(f"🏢 STEP 5: Company Research (Perplexity)")
            print(f"{'='*60}")

            step_status["company_research"] = "in_progress"

            # Identify contacts that still need company research
            # (For resume: skip contacts that already have company_research)
            contacts_to_research = df[
                (df['company_research'].isna()) | (df['company_research'] == '') | (df['company_research'] == 'pending')
            ]

            # Get unique companies that need research (only from contacts that need it)
            unique_companies_to_research = contacts_to_research['company_domain'].dropna().unique()
            if len(contacts_to_research) < len(df):
                print(f"   Resuming: {len(df) - len(contacts_to_research)} contacts already have research")
            print(f"   Researching {len(unique_companies_to_research)} unique companies for {len(contacts_to_research)} contacts...")
            print()

            # Research companies ONE TIME EACH, then fill all contacts from that company
            company_research_cache = {}  # domain -> research result

            if len(unique_companies_to_research) > 0:
                # Helper function to research a single company (not contact)
                def research_single_company(domain: str) -> tuple:
                    """Research one company and return (domain, result)"""
                    # Get company name from first contact with this domain (with safety check)
                    company_records = df[df['company_domain'] == domain]['company_name']
                    if len(company_records) > 0:
                        company_name = company_records.iloc[0]
                    else:
                        # Fallback to domain if no company name found
                        company_name = domain
                    result = self.researcher.research_company(company_name, domain)
                    return domain, result

                # Research companies in parallel (one call per company, not per contact!)
                completed = 0
                total_companies = len(unique_companies_to_research)

                with ThreadPoolExecutor(max_workers=min(max_workers, 5)) as executor:  # Limit to 5 for Perplexity rate limits
                    future_to_domain = {
                        executor.submit(research_single_company, domain): domain
                        for domain in unique_companies_to_research
                    }

                    for future in as_completed(future_to_domain):
                        # Check for cancel
                        if self._cancelled:
                            print(f"\n   ⚠️ Cancelled - saving checkpoint...")
                            self.checkpoint_mgr.update_checkpoint(self._current_job_id, df, 5, step_status)
                            raise InterruptedError("Job cancelled by user")

                        try:
                            domain, result = future.result()
                            company_research_cache[domain] = result
                            completed += 1
                            try:
                                print(f"   ✅ Researched {completed}/{total_companies} companies...")
                            except (ValueError, IOError):
                                pass
                        except Exception as e:
                            domain = future_to_domain[future]
                            company_research_cache[domain] = f"Error: {str(e)}"
                            completed += 1

                # Now fill all contacts with their company's research
                for idx, row in contacts_to_research.iterrows():
                    domain = row.get('company_domain', '')
                    if domain and domain in company_research_cache:
                        df.at[idx, "company_research"] = company_research_cache[domain]
                    else:
                        df.at[idx, "company_research"] = "No research available"

                print(f"   ✅ Applied research to {len(contacts_to_research)} contacts")

            print()

            # Mark step complete
            step_status["company_research"] = "complete"

        # ============================================================
        # Summary & Cleanup
        # ============================================================
        try:
            print(f"{'='*60}")
            print(f"✅ PHASE 2 COMPLETE")
            print(f"{'='*60}")
            print(f"📊 Pipeline Summary:")
            print(f"   Started with: {original_count} contacts")
            if enrich_emails:
                print(f"   After email enrichment & verification: {count_after_email} contacts")
            print(f"   After LinkedIn scraping: {count_after_linkedin} contacts")
            if verify_current_employment:
                print(f"   After employment verification: {count_after_employment} contacts")
            if min_profile_quality and min_profile_quality > 1:
                print(f"   After profile quality filter: {len(df)} contacts")
            print(f"   Final output: {len(df)} fully enriched contacts")

            # Show quality distribution
            if len(df) > 0:
                quality_counts = df['profile_quality_rating'].value_counts()
                high_quality = quality_counts.get('excellent', 0) + quality_counts.get('high', 0)
                if high_quality > 0:
                    print(f"🌟 High-quality profiles: {high_quality}")
            print()

            # Delete checkpoint on successful completion
            if self._current_job_id:
                self.checkpoint_mgr.delete_checkpoint(self._current_job_id)
                print(f"🗑️ Checkpoint cleaned up (job complete)")
                print()

        except (ValueError, IOError):
            pass

        return df

    def export_enriched_csv(self, df: pd.DataFrame, filename: str = None) -> str:
        """Export enriched DataFrame to CSV"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"phase2_enriched_{timestamp}.csv"

        output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        # Use QUOTE_NONNUMERIC to properly escape multi-line fields (personal_research, company_research)
        # This prevents CSV column misalignment from commas and newlines in text fields
        df.to_csv(filepath, index=False, quoting=csv.QUOTE_NONNUMERIC)

        try:
            print(f"💾 Exported to: {filepath}")
            print(f"📋 Columns: {', '.join(df.columns)}")
            print()
        except (ValueError, IOError):
            # Suppress I/O errors when stdout is closed (happens in subprocess mode)
            pass

        return filepath


def main():
    """
    Main execution - example usage
    """
    import sys

    # Check for input file
    if len(sys.argv) < 2:
        print("Usage: python main.py <phase1_csv_file> [OPTIONS]")
        print("\nOptions:")
        print("  --enrich-emails     Spend Apollo credits to get real emails")
        print("  --verify-emails     Verify emails with Instantly.ai (requires --enrich-emails)")
        print("  --max N             Limit to N contacts (for testing)")
        print("  --min-score N       Only process contacts with fit_score >= N")
        print("  --workers N         Number of parallel workers (default: 30)")
        print("  --sequential        Use sequential processing instead of parallel")
        print("\nExamples:")
        print("  python main.py input.csv --max 5")
        print("  python main.py input.csv --enrich-emails --min-score 7")
        print("  python main.py input.csv --enrich-emails --verify-emails")
        print("  python main.py input.csv --workers 30")
        print("  python main.py input.csv --sequential  # Slower, but easier to debug")
        sys.exit(1)

    input_csv = sys.argv[1]
    enrich_emails = "--enrich-emails" in sys.argv
    use_parallel = "--sequential" not in sys.argv  # Parallel by default
    max_contacts = None
    min_score = None
    max_workers = 12  # Conservative for Apify limits (32 concurrent / 2 jobs per contact)

    # Parse args
    for i, arg in enumerate(sys.argv):
        if arg == "--max" and i + 1 < len(sys.argv):
            max_contacts = int(sys.argv[i + 1])
        if arg == "--min-score" and i + 1 < len(sys.argv):
            min_score = int(sys.argv[i + 1])
        if arg == "--workers" and i + 1 < len(sys.argv):
            max_workers = int(sys.argv[i + 1])

    # Run enrichment
    orchestrator = Phase2Orchestrator()

    if use_parallel:
        # Use parallel processing (FASTER - 3-5x speedup)
        # Note: enrich_emails=True automatically enables waterfall with verification
        enriched_df = orchestrator.enrich_contacts_batch_parallel(
            input_csv=input_csv,
            enrich_emails=enrich_emails,
            max_contacts=max_contacts,
            min_score=min_score,
            max_workers=max_workers
        )
    else:
        # Use sequential processing (for debugging)
        enriched_df = orchestrator.enrich_contacts_batch(
            input_csv=input_csv,
            enrich_emails=enrich_emails,
            max_contacts=max_contacts,
            min_score=min_score
        )

    # Export
    orchestrator.export_enriched_csv(enriched_df)


if __name__ == "__main__":
    main()
