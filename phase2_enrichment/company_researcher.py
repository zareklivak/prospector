"""
Company research using Perplexity AI
Researches company once, caches for all contacts at same company
Gathers deep intelligence about target companies for Waypoint sales context
"""

import requests
import threading
from typing import Dict
from config import PERPLEXITY_API_KEY


class CompanyResearcher:
    """Uses Perplexity to research companies - focused on target company intelligence"""

    def __init__(self, api_key: str = PERPLEXITY_API_KEY):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai"
        self.cache = {}  # Cache company research to avoid duplicate calls
        self.cache_lock = threading.Lock()  # Thread-safe cache access for parallel processing

    def research_company(self, company_name: str, company_domain: str) -> str:
        """
        Deep intelligence gathering about target company
        Focus: operations, technology, strategic initiatives
        Output: Detailed company profile for personalizing outreach

        Returns cached results if company was already researched.
        Thread-safe caching ensures research happens only once per company,
        even with parallel processing of multiple contacts.
        """
        # Defensive: Handle missing/NaN company_domain (convert float to string)
        company_domain_str = str(company_domain) if company_domain and str(company_domain) != 'nan' else ""

        # Skip research if no domain available
        if not company_domain_str:
            return f"Unable to research {company_name}: no company domain provided"

        cache_key = company_domain_str.lower()

        # Thread-safe cache check
        with self.cache_lock:
            if cache_key in self.cache:
                try:
                    print(f"   💾 Using cached research for: {company_name}")
                except (ValueError, IOError):
                    pass  # Suppress I/O errors when stdout is closed
                return self.cache[cache_key]

        # Research not cached - do the API call (outside lock to allow parallel requests)
        try:
            print(f"   🔍 Researching {company_name} for Waypoint context...")
        except (ValueError, IOError):
            pass  # Suppress I/O errors when stdout is closed

        # Deep company intelligence gathering for Waypoint selling context
        prompt = f"""Research {company_name} (website: {company_domain_str}) and provide detailed intelligence about their operations, technology, and strategic initiatives. This research will be used to personalize outreach to their operations, IT, and innovation leaders.

**CRITICAL FIRST STEP - Company Type Classification (Two-Level System):**
Begin your research by explicitly classifying the company at TWO levels:

**Level 1 - High-Level Bucket (choose ONE primary category):**
- **CARRIER** (asset-based transportation - owns trucks/ships/planes)
- **BROKER** (non-asset freight brokerage, digital freight matching)
- **3PL** (third-party logistics, warehousing, fulfillment, distribution)
- **FORWARDER** (freight forwarding, customs brokerage, international logistics)
- **MANUFACTURER** (manufacturing company with integrated logistics)
- **RETAILER** (retail company with supply chain operations)
- **DISTRIBUTOR** (wholesale distribution, food/beverage distribution)
- **TECHNOLOGY** (logistics software, TMS/WMS platforms, freight tech)
- **OTHER** (if none fit, specify what they are)

**Level 2 - Specific Business Model:**
Be as precise and specific as possible about their exact service offerings and business model.

Examples of specific classifications:
- Dedicated truckload carrier, LTL carrier, refrigerated carrier, flatbed specialist
- Ocean carrier, LCL carrier, intermodal provider, drayage provider
- Digital freight brokerage, traditional brokerage, load board platform
- Temperature-controlled warehousing 3PL, e-commerce fulfillment 3PL, contract logistics
- International freight forwarder (air/ocean), customs broker, NVOCC
- Final mile delivery, last mile provider, parcel/package delivery
- Cold chain distributor, foodservice distributor, beverage distributor
- Any other specific logistics/supply chain business model

**Output Format - Start your research with this structure:**
"[Company Name] is a [HIGH-LEVEL BUCKET] company, specifically a [SPECIFIC BUSINESS MODEL]..."

**Examples:**
- "CRST is a CARRIER, specifically a dedicated truckload carrier and expedited team driver specialist..."
- "Americold is a 3PL, specifically a temperature-controlled warehousing provider and cold chain logistics specialist..."
- "C.H. Robinson is a BROKER, specifically a non-asset freight brokerage and third-party logistics provider..."
- "Maersk is a CARRIER, specifically an ocean carrier and integrated container logistics provider..."

**Research Focus - Gather Maximum Intelligence with BOTH Qualitative & Quantitative Metrics:**

1. **Operations & Logistics Scale** (Focus on UNIQUE aspects and SPECIFIC numbers)
   - Exact fleet size, number of facilities, shipment volumes, geographic footprint
   - Division names, business units, service lines (dedicated, brokerage, intermodal, etc.)
   - Operational metrics: on-time delivery %, utilization rates, cost per mile, any KPIs mentioned
   - What makes their operations UNIQUE or DIFFERENT from competitors?
   - Any operational challenges: labor shortages, capacity issues, seasonal fluctuations
   - Customer service operations and communication workflows
   - Unique service offerings or specialized capabilities

2. **Technology Infrastructure & Systems** (Name specific platforms and unique tech)
   - Specific TMS platforms they use (name them - e.g., "Werner EDGE®", "McLeod LoadMaster", etc.)
   - Other technology platforms: ERP, WMS, telematics, tracking systems
   - IT infrastructure: cloud providers, API strategies, integration capabilities
   - Recent technology investments or modernization projects (name specific initiatives)
   - Technology partnerships or vendor relationships
   - Proprietary systems or unique technology differentiators

3. **Digital Transformation & Innovation** (Focus on what makes them innovative/unique)
   - Automation projects: RPA, AI/ML initiatives, chatbots, voice systems
   - Digital transformation roadmap or strategy (use actual program names if mentioned)
   - Innovation labs, pilot programs, or emerging tech experiments
   - Mobile apps, customer portals, driver-facing technology
   - Data analytics, business intelligence, or IoT implementations
   - Industry-leading innovations or unique digital capabilities

4. **Strategic Priorities & Recent News** (Quantitative + qualitative insights)
   - Growth plans: expansion, new facilities, M&A activity
   - Operational excellence programs (name specific initiatives)
   - Customer experience or service quality improvements
   - Financial performance: revenue, growth rate, profitability trends (2023-2025)
   - Leadership changes: new hires in Operations, IT, Innovation, or C-suite
   - What makes their strategy UNIQUE in the market?

5. **Communication-Heavy Processes** (important context)
   - Dispatch operations and check call processes
   - Load tracking and status update workflows
   - Appointment scheduling and detention management
   - Payment follow-ups and billing operations
   - Customer service volume and structure

**Critical Requirements:**
- **START with company type classification** (e.g., "Americold is a temperature-controlled warehousing 3PL...")
- Use ONLY specific proper nouns (system names, initiative names, executive names, division names)
- Include BOTH qualitative insights (what makes them unique) AND quantitative metrics (exact numbers)
- Focus on UNIQUE/DIFFERENTIATING aspects - what sets them apart from competitors?
- Focus entirely on THE COMPANY - this is intelligence gathering about them, not about us
- Write 4-5 detailed paragraphs (400-500 words total)
- Professional, factual tone - like a briefing document
- Recent information only (2023-2025)
- If you don't find specific details, focus on industry context and what's typical for their size/sector"""

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a business intelligence researcher specializing in logistics, supply chain, and transportation companies. Provide detailed, specific intelligence with proper nouns, metrics, and concrete details. Focus on the target company's operations, technology, and strategy."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.2,
                    "max_tokens": 1200
                },
                timeout=90
            )

            if response.status_code != 200:
                error_msg = f"API error: {response.status_code}"
                try:
                    print(f"   ❌ {error_msg}")
                except (ValueError, IOError):
                    pass  # Suppress I/O errors when stdout is closed
                return error_msg

            data = response.json()
            research = data["choices"][0]["message"]["content"]

            # Cache the result (thread-safe)
            with self.cache_lock:
                self.cache[cache_key] = research

            try:
                print(f"   ✅ Research complete ({len(research)} chars)")
            except (ValueError, IOError):
                pass  # Suppress I/O errors when stdout is closed
            return research

        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            try:
                print(f"   ❌ {error_msg}")
            except (ValueError, IOError):
                pass  # Suppress I/O errors when stdout is closed
            return error_msg
