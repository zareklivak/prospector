"""
LinkedIn enrichment via Apify actors
Handles profile scraping and post collection

OPTIMIZED: Added timeout configuration and retry logic to prevent hanging.
"""

from typing import Dict, List
from apify_client import ApifyClient
from config import (
    APIFY_API_TOKEN,
    LINKEDIN_POSTS_ACTOR,
    LINKEDIN_PROFILE_ACTOR,
    MAX_POSTS_PER_CONTACT
)
import logging
import os
import sys
import time

# Suppress Apify SDK verbose logging (container pulls, system info, etc.)
logging.getLogger('apify_client').setLevel(logging.ERROR)
logging.getLogger('apify').setLevel(logging.ERROR)
logging.getLogger('apify_client.log').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.ERROR)
logging.getLogger('httpcore').setLevel(logging.ERROR)

# Suppress Apify's direct stdout logging
os.environ['APIFY_LOG_LEVEL'] = 'ERROR'

# Timeout and retry configuration
ACTOR_TIMEOUT_SECS = 120  # Max time to wait for actor to complete
MAX_RETRIES = 2  # Number of retries on timeout/failure
RETRY_DELAY = 5  # Seconds between retries


class ApifyEnricher:
    """Handles LinkedIn enrichment via Apify actors"""

    def __init__(self, api_token: str = APIFY_API_TOKEN):
        self.client = ApifyClient(api_token, max_retries=3, timeout_secs=ACTOR_TIMEOUT_SECS)

    def scrape_linkedin_posts(self, linkedin_url: str) -> Dict:
        """
        Scrape recent LinkedIn posts using ApifyClient
        Cost safety: Limits to MAX_POSTS_PER_CONTACT (default: 5) posts
        Actor: apimaestro/linkedin-profile-posts

        OPTIMIZED: Added retry logic for timeouts.

        Returns:
            {"posts": [...], "error": None/str}
        """
        if not linkedin_url or "linkedin.com" not in linkedin_url:
            return {"posts": [], "error": "Invalid LinkedIn URL"}

        # Extract username from LinkedIn URL
        # e.g. "https://www.linkedin.com/in/eric-downing-a135614" -> "eric-downing-a135614"
        username = linkedin_url.rstrip('/').split('/')[-1]

        if not username:
            return {"posts": [], "error": "Could not extract username from URL"}

        # Use correct parameters for apimaestro/linkedin-profile-posts actor
        run_input = {
            "profileUrl": linkedin_url,  # Full LinkedIn URL
            "username": username,         # Extracted username
            "total_posts": MAX_POSTS_PER_CONTACT  # Limit to 5 posts (enables auto-pagination with limit)
        }

        last_error = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                # Run actor and wait for completion (with timeout)
                run = self.client.actor(LINKEDIN_POSTS_ACTOR).call(
                    run_input=run_input,
                    timeout_secs=ACTOR_TIMEOUT_SECS
                )
                # Get results from dataset
                items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

                # Safety limit: Only use first MAX_POSTS_PER_CONTACT posts
                posts = items[:MAX_POSTS_PER_CONTACT]

                return {"posts": posts, "error": None}

            except Exception as e:
                last_error = str(e)
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                    continue

        return {"posts": [], "error": f"Exception after {MAX_RETRIES + 1} attempts: {last_error}"}

    def scrape_linkedin_profile(self, linkedin_url: str) -> Dict:
        """
        Scrape LinkedIn profile data using ApifyClient
        Gets: headline, experience, education, about section, skills, connections
        Actor: dev_fusion/linkedin-profile-scraper

        OPTIMIZED: Added retry logic for timeouts.

        Returns:
            {"profile": {...}, "error": None/str}
        """
        if not linkedin_url or "linkedin.com" not in linkedin_url:
            return {"profile": {}, "error": "Invalid LinkedIn URL"}

        run_input = {
            "profileUrls": [linkedin_url],
            "fastMode": False  # Get full profile data
        }

        last_error = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                # Run actor and wait for completion (with timeout)
                run = self.client.actor(LINKEDIN_PROFILE_ACTOR).call(
                    run_input=run_input,
                    timeout_secs=ACTOR_TIMEOUT_SECS
                )
                # Get results from dataset
                items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

                # Extract profile (should be first item)
                profile = {}
                if items and len(items) > 0:
                    profile = items[0]

                return {"profile": profile, "error": None}

            except Exception as e:
                last_error = str(e)
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                    continue

        return {"profile": {}, "error": f"Exception after {MAX_RETRIES + 1} attempts: {last_error}"}
