"""
Configuration file for Phase 1 Apollo Scraper
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# API Keys
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY", "your_apollo_api_key_here")

# Apollo API Settings
APOLLO_BASE_URL = "https://api.apollo.io/v1"
APOLLO_SEARCH_ENDPOINT = "/mixed_people/search"
APOLLO_ENRICH_ENDPOINT = "/people/match"

# Search Parameters - Apollo seniority filters
# These are the available Apollo seniority levels we support
AVAILABLE_SENIORITIES = {
    "c_suite": ["c_suite", "head"],  # C-Suite/Head grouped together
    "vp": ["vp"],
    "director": ["director"],
    "manager": ["manager"]
}

# Default seniorities (Director+ without Manager)
DEFAULT_SENIORITIES = ["director", "vp", "head", "c_suite"]

# Legacy constant for backwards compatibility
SENIORITIES = DEFAULT_SENIORITIES

MAX_CONTACTS_PER_COMPANY = 2000  # Maximum to pull from Apollo initially (configurable via frontend)
DEFAULT_MAX_INITIAL_SCRAPE = 2000  # Default for initial scrape before scoring
DEFAULT_CONTACTS_TO_EXPORT = 20  # Default number of top-ranked contacts to export

# Scoring Configuration
SCORING_KEYWORDS = {
    # High priority - AI/Innovation/Transformation (Score: 8-10)
    "ai": 10,
    "artificial intelligence": 10,
    "innovation": 9,
    "transformation": 9,
    "digital": 8,
    "automation": 9,
    "technology": 8,
    
    # Operations - High value (Score: 7-9)
    "operations": 8,
    "supply chain": 9,
    "logistics": 9,
    "warehouse": 8,
    "fulfillment": 8,
    "distribution": 8,
    
    # Strategic roles (Score: 6-8)
    "strategy": 7,
    "business development": 7,
    "growth": 7,
    "product": 7,
    "engineering": 7,
    "information technology": 7,
    "it": 6,
    
    # Lower priority (Score: 3-5)
    "finance": 4,
    "financial": 4,
    "accounting": 3,
    "human resources": 3,
    "hr": 3,
    "legal": 3,
    "admin": 2,
}

# Role title modifiers (bonus points)
TITLE_MODIFIERS = {
    "chief": 2,  # CXO roles get +2
    "vp": 1,
    "vice president": 1,
    "head": 1,
    "director": 0,
}

# Minimum score threshold
MIN_SCORE = 3
