"""
Apollo API Scraper
Handles API calls to Apollo.io for searching and retrieving contacts
"""

import requests
import time
import pandas as pd
import os
from typing import List, Dict, Optional
from openai import OpenAI
from config import (
    APOLLO_API_KEY,
    APOLLO_BASE_URL,
    APOLLO_SEARCH_ENDPOINT,
    DEFAULT_SENIORITIES,
    MAX_CONTACTS_PER_COMPANY
)


class ApolloScraper:
    def __init__(self, api_key: str = APOLLO_API_KEY, seniorities: Optional[List[str]] = None, include_all_contacts: bool = False):
        self.api_key = api_key
        self.base_url = APOLLO_BASE_URL
        self.headers = {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
            'X-Api-Key': self.api_key
        }
        # Seniorities to filter by (use default if not provided)
        self.seniorities = seniorities if seniorities else DEFAULT_SENIORITIES
        # Include all contacts (even without emails) for waterfall enrichment
        self.include_all_contacts = include_all_contacts
        # Initialize OpenAI client for company name shortening
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        # Cache for shortened names to avoid redundant API calls
        self._name_cache = {}
    
    def search_people(
        self,
        company_domain: str,
        max_results: int = MAX_CONTACTS_PER_COMPANY,
        per_page: int = 100
    ) -> List[Dict]:
        """
        Search for people at a company with Director+ seniority

        If include_all_contacts is False (default): Only returns contacts with available emails
        If include_all_contacts is True (waterfall mode): Returns all contacts for waterfall enrichment
        """
        all_contacts = []
        page = 1

        payload = {
            "page": page,
            "per_page": per_page,
            "q_organization_domains": company_domain,  # Fixed: q_ prefix required
            "person_seniorities": self.seniorities,
        }

        # Only filter by email status if NOT in waterfall mode
        if not self.include_all_contacts:
            payload["contact_email_status"] = ["verified", "guessed"]  # Only contacts with emails

        print(f"\n🔍 Searching Apollo for contacts at {company_domain}...")
        print(f"   Filtering for: {', '.join(self.seniorities)} levels")
        if self.include_all_contacts:
            print(f"   Mode: Waterfall enrichment (including contacts without emails)")
        print(f"   Max contacts: {max_results}")
        
        while len(all_contacts) < max_results:
            try:
                payload["page"] = page
                response = requests.post(
                    f"{self.base_url}{APOLLO_SEARCH_ENDPOINT}",
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code != 200:
                    print(f"❌ Error: {response.status_code} - {response.text}")
                    break
                
                data = response.json()
                people = data.get('people', [])
                
                if not people:
                    print(f"✓ No more contacts found (stopped at page {page})")
                    break
                
                all_contacts.extend(people)
                print(f"   Page {page}: Retrieved {len(people)} contacts (Total: {len(all_contacts)})")

                # Check if we've reached the end
                pagination = data.get('pagination', {})
                total_pages = pagination.get('total_pages', 1)

                if page >= total_pages:
                    print(f"✓ Reached last page ({page}/{total_pages})")
                    break

                page += 1
                
                # Respect rate limits
                time.sleep(0.5)
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Request failed: {str(e)}")
                break
        
        # Trim to max_results
        all_contacts = all_contacts[:max_results]
        print(f"\n✓ Found {len(all_contacts)} total contacts with emails\n")
        
        return all_contacts
    
    def shorten_company_name(self, company_name: str) -> str:
        """
        Use LLM to intelligently extract the core brand name for casual email usage
        Examples:
            "Publix Supermarkets" → "Publix"
            "Albertsons Companies, Inc." → "Albertsons"
            "FedEx Corporation" → "FedEx"
            "Werner Enterprises, Inc." → "Werner"
            "DHL Supply Chain" → "DHL"
        """
        if not company_name:
            return ""

        # Check cache first
        if company_name in self._name_cache:
            return self._name_cache[company_name]

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You extract the core brand name from company legal names for casual email usage.

Rules:
1. Remove all legal suffixes (Inc., LLC, Corp., Ltd., Corporation, Company, Companies, etc.)
2. Remove generic business descriptors (Services, Solutions, Logistics, Group, International, Worldwide, etc.)
3. Keep only the PRIMARY brand name that people would use in conversation
4. For multi-word brands, keep ONLY the distinctive brand name (e.g., "Publix Supermarkets" → "Publix", not "Publix Supermarkets")
5. Output ONLY the shortened name, nothing else

Examples:
- "Publix Supermarkets" → "Publix"
- "Albertsons Companies, Inc." → "Albertsons"
- "FedEx Corporation" → "FedEx"
- "Werner Enterprises, Inc." → "Werner"
- "Gordon Food Service" → "Gordon"
- "DHL Supply Chain" → "DHL"
- "CH Robinson Worldwide" → "CH Robinson"
- "J.B. Hunt Transport Services, Inc." → "J.B. Hunt"
- "Old Dominion Freight Line, Inc." → "Old Dominion"
- "Schneider National, Inc." → "Schneider"
- "XPO Logistics" → "XPO"
- "Hub Group" → "Hub"
- "Penske Truck Leasing Co., L.P." → "Penske"""
                    },
                    {
                        "role": "user",
                        "content": company_name
                    }
                ],
                max_tokens=20,
                temperature=0
            )

            shortened = response.choices[0].message.content.strip()

            # Cache the result
            self._name_cache[company_name] = shortened

            return shortened

        except Exception as e:
            print(f"   ⚠️  LLM shortening failed for '{company_name}': {e}")
            # Fallback: basic suffix removal
            for suffix in [", Inc.", " Inc.", ", LLC", " LLC", " Corporation", ", Corporation", " Corp.", " Companies", " Company"]:
                if company_name.endswith(suffix):
                    return company_name[:-len(suffix)].strip()
            return company_name

    def contacts_to_dataframe(self, contacts: List[Dict], searched_domain: str = None) -> pd.DataFrame:
        """
        Convert Apollo API response to a clean pandas DataFrame

        Args:
            contacts: List of contact dicts from Apollo API
            searched_domain: The domain that was searched for (fallback if Apollo doesn't return primary_domain)
        """
        if not contacts:
            return pd.DataFrame()

        rows = []
        for contact in contacts:
            # Extract company name
            company_name = contact.get('organization', {}).get('name', '')

            # Get primary_domain from Apollo, fallback to searched domain if not available
            primary_domain = contact.get('organization', {}).get('primary_domain')
            if not primary_domain and searched_domain:
                primary_domain = searched_domain

            # Extract relevant fields
            row = {
                'first_name': contact.get('first_name', ''),
                'last_name': contact.get('last_name', ''),
                'title': contact.get('title', ''),
                'email': contact.get('email', ''),
                'email_status': contact.get('email_status', ''),
                'linkedin_url': contact.get('linkedin_url', ''),
                'company_name': company_name,
                'company_name_for_emails': self.shorten_company_name(company_name),
                'company_domain': primary_domain or '',
                'company_linkedin': contact.get('organization', {}).get('linkedin_url', ''),
                'seniority': contact.get('seniority', ''),
                'departments': ', '.join(contact.get('departments', [])) if contact.get('departments') else '',
                'city': contact.get('city', ''),
                'state': contact.get('state', ''),
                'country': contact.get('country', ''),
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)

        # Filter by email status unless in waterfall mode
        if not self.include_all_contacts:
            # Keep contacts with verified OR guessed emails
            df = df[df['email_status'].isin(['verified', 'guessed'])].reset_index(drop=True)
            print(f"📊 Converted to DataFrame: {len(df)} contacts with verified/guessed emails")
        else:
            # Waterfall mode: keep all contacts (even without emails)
            df = df.reset_index(drop=True)
            has_email = df['email_status'].isin(['verified', 'guessed']).sum()
            no_email = len(df) - has_email
            print(f"📊 Converted to DataFrame: {len(df)} contacts ({has_email} with emails, {no_email} without)")

        return df
    
    def scrape_company(
        self,
        company_domain: str,
        max_results: int = MAX_CONTACTS_PER_COMPANY
    ) -> pd.DataFrame:
        """
        Main method: Scrape a company and return DataFrame
        """
        contacts = self.search_people(company_domain, max_results)
        df = self.contacts_to_dataframe(contacts, searched_domain=company_domain)
        return df


if __name__ == "__main__":
    # Test the scraper
    scraper = ApolloScraper()
    
    # Test with a sample domain
    test_domain = "anthropic.com"  # Replace with actual test domain
    df = scraper.scrape_company(test_domain, max_results=50)
    
    if not df.empty:
        print(f"\n✓ Successfully scraped {len(df)} contacts")
        print(f"\nSample data:")
        print(df[['first_name', 'last_name', 'title', 'email']].head())
    else:
        print("\n❌ No contacts found")
