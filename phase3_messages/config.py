"""
Configuration for Phase 3 Message Generation
"""

import os
from dotenv import load_dotenv

# Load from project root .env
load_dotenv()

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# LLM Provider Settings - Dual Model Support
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"
OPENAI_MODEL = "gpt-4o"  # GPT-4o for speed and quality
TEMPERATURE = 0.7  # Creativity level (0.5-0.9)
MAX_RETRIES = 3  # Retry failed generations

# Dual LLM Configuration
USE_DUAL_LLMS = True  # Use both Claude and OpenAI in parallel
CLAUDE_WORKERS = 8  # Parallel Claude workers (increased from 3)
OPENAI_WORKERS = 8  # Parallel OpenAI workers (increased from 3)

# Generation Mode
MESSAGE_MODE = "email"  # "email" or "linkedin"

# Quality Control
MIN_PERSONALIZATION_SCORE = 7  # Out of 10
FLAG_GENERIC_PHRASES = True
VALIDATE_QUALITY = True

# Generic phrases to avoid (flags for quality check)
GENERIC_PHRASES = [
    "i came across your profile",
    "i hope this email finds you well",
    "i'd love to connect",
    "we help companies like yours",
    "i noticed you work in",
    "touching base",
    "just reaching out",
    "wanted to reach out",
    "hope you're doing well",
    "checking in",
]

# Waypoint Context (for messaging)
COMPANY_NAME = "Waypoint"
COMPANY_PRODUCT = "Agentic AI workers for supply chain operations"

VALUE_PROPS = {
    "core": "AI operating system that handles communication-heavy logistics workflows",
    "key_benefits": [
        "Handles communication-heavy processes (not just data processing)",
        "Integrates with existing systems (no rip-and-replace)",
        "Built specifically for logistics (not generic AI)",
        "Reduces headcount needs while improving service quality",
        "Scales globally across time zones and languages"
    ],
    "use_cases": [
        "Dispatch automation",
        "Customer service",
        "Appointment scheduling",
        "Load tracking",
        "Detention management",
        "Billing inquiries"
    ]
}

PROOF_POINTS = [
    "Handles thousands of customer interactions daily",
    "Reduces response times from hours to minutes",
    "Works 24/7 across global operations",
    "Learns company-specific workflows",
    "No dedicated IT resources needed to deploy"
]

# Message Length Requirements
EMAIL_LENGTH = {"min": 150, "max": 250}  # Words
LINKEDIN_LENGTH = {"min": 100, "max": 150}  # Words

# Output Settings
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
