"""
Configuration for Phase 2 Enrichment
"""

import os
from dotenv import load_dotenv

# Load from project root .env
load_dotenv()

# API Keys
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Waterfall enrichment API keys
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")
FINDYMAIL_API_KEY = os.getenv("FINDYMAIL_API_KEY")

# Apify Actor IDs (use slash format for ApifyClient)
# Posts: apimaestro/linkedin-profile-posts (working with total_posts parameter)
# Profile: dev_fusion/linkedin-profile-scraper (working with profileUrls)
LINKEDIN_POSTS_ACTOR = "apimaestro/linkedin-profile-posts"
LINKEDIN_PROFILE_ACTOR = "dev_fusion/linkedin-profile-scraper"

# Cost controls
MAX_POSTS_PER_CONTACT = 5  # Limit posts to keep costs low
MAX_WAIT_TIME = 60  # Max seconds to wait for Apify actor runs

# Rate limiting
API_DELAY_SECONDS = 2  # Delay between API calls to be nice to services
