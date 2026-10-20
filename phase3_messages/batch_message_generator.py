"""
OPTIMIZED Batch Message Generation - All 4 messages in 1 API call
Generates personalized 4-step sequences efficiently
Now using JSON templates for easy frontend editing!
DUAL LLM SUPPORT: Can use Claude or OpenAI in parallel!
"""

import anthropic
from openai import OpenAI
import random
from typing import Dict, Optional, List
import pandas as pd

from config import ANTHROPIC_API_KEY, OPENAI_API_KEY, CLAUDE_MODEL, OPENAI_MODEL, TEMPERATURE
from prompts.new_system_instructions import SYSTEM_PROMPT
from use_case_matcher import UseCaseMatcher
from template_manager import TemplateManager


class BatchMessageGenerator:
    """
    Generates all 4 messages in a single API call for maximum efficiency
    Uses JSON templates that can be edited via frontend
    DUAL LLM: Supports both Claude and OpenAI for parallel generation
    """

    def __init__(self, llm_provider: str = "claude", template_file: Optional[str] = None, custom_template_path: Optional[str] = None, subject_line_config: Optional[Dict] = None):
        """
        Initialize generator with specified LLM provider

        Args:
            llm_provider: "claude" or "openai"
            template_file: Optional custom template file path (deprecated, use custom_template_path)
            custom_template_path: Optional custom template file path (per-run override)
            subject_line_config: Optional config for subject line generation (email mode only)
                                 {"style": "question"|"direct"|"curiosity"|"value"|"custom", "customPrompt": str}
        """
        self.llm_provider = llm_provider
        self.use_case_matcher = UseCaseMatcher()
        # Use custom_template_path if provided, otherwise fall back to template_file
        self.template_file = custom_template_path or template_file
        self.subject_line_config = subject_line_config

        # Initialize appropriate client
        if llm_provider == "claude":
            self.model = CLAUDE_MODEL
            self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        elif llm_provider == "openai":
            self.model = OPENAI_MODEL
            self.client = OpenAI(api_key=OPENAI_API_KEY)
        else:
            raise ValueError(f"Unknown LLM provider: {llm_provider}. Use 'claude' or 'openai'")

    def _shorten_company_name(self, company_name: str) -> str:
        """
        DEPRECATED: This method is no longer used.
        We now use the 'company_name_for_emails' column from Phase 1,
        which was intelligently shortened using LLM-based extraction.

        Kept for backwards compatibility only.
        """
        if "DSV" in company_name or "MSC Mediterranean Shipping" in company_name:
            return company_name.split()[0] if company_name.split() else company_name

        words = company_name.split()
        if len(words) > 2:
            if len(words[0]) <= 4 and words[0].isupper():
                return words[0]
            return words[0]

        return company_name

    def generate_batch_sequence(self, contact_row: pd.Series, mode: str = "email", company_type_override: Optional[str] = None) -> Dict[str, str]:
        """
        Generate all 4 messages in ONE API call

        Args:
            contact_row: Pandas Series with contact data
            mode: "email" or "linkedin"
            company_type_override: Optional industry override for testing/forcing specific use cases
                                   (e.g., "broker", "carrier", "air freight", "commercial airline")
                                   When provided, skips auto-detection and uses this industry

        Returns:
            Dict with message_1, message_2, message_3, message_4
        """

        # Prepare contact data with defensive type checking
        contact_data = {
            'first_name': str(contact_row['first_name']),
            'last_name': str(contact_row['last_name']),
            'title': str(contact_row['title']),
            'company_name': str(contact_row['company_name']),
            'company_name_for_emails': str(contact_row.get('company_name_for_emails', contact_row['company_name'])),
            'fit_score': contact_row['fit_score'],
            'personal_research': str(contact_row.get('personal_research', 'No personal research available')),
            'company_research': str(contact_row.get('company_research', 'No company research available'))
        }

        # Detect company type (with optional override from frontend)
        company_type, _ = self.use_case_matcher.detect_company_type(
            contact_data['company_research'],
            contact_data['title'],
            override=company_type_override
        )
        if company_type_override:
            print(f"🎯 Using industry override: {company_type_override} → {company_type}")

        # Get intelligent use case selection
        use_cases = self.use_case_matcher.get_intelligent_use_cases(
            company_type=company_type,
            personal_research=contact_data['personal_research'],
            title=contact_data['title'],
            count=4
        )

        # Get value propositions for this vertical (get 4 to have enough for both short and long)
        value_props = self.use_case_matcher.get_value_props(
            company_type=company_type,
            title=contact_data['title'],
            count=4
        )

        # Format use cases - SHORT (2) and LONG (4) versions
        use_cases_short = self.use_case_matcher.format_use_cases_inline(use_cases[:2])
        use_cases_long = self.use_case_matcher.format_use_cases_inline(use_cases[:4])

        # DEPRECATED: Keep old variables for backwards compatibility
        use_cases_inline = use_cases_long  # Maps to long version
        use_cases_examples = self.use_case_matcher.format_use_cases_inline(use_cases[1:4])

        # Format value props - SHORT (1) and LONG (3-4) versions
        value_prop_short = value_props[0] if value_props else "operational efficiency"
        value_prop_long = self._format_value_props_conversational(value_props[:3]) if value_props else "operational efficiency and better visibility"

        # DEPRECATED: Keep old variable for backwards compatibility
        value_prop_selection = value_prop_long  # Maps to long version

        # Use pre-generated shortened company name from Phase 1 (company_name_for_emails)
        # This was already intelligently shortened in Phase 1 using LLM, no need to re-process
        company_name_short = contact_data['company_name_for_emails']

        # Initialize TemplateManager with mode-specific template
        template_mgr = TemplateManager(mode=mode, template_file=self.template_file)

        # Get system prompt from template (if unified format) or use default
        custom_system_prompt = template_mgr.get_system_prompt()
        system_prompt_to_use = custom_system_prompt if custom_system_prompt else SYSTEM_PROMPT

        # Build batch prompt - use unified or old format method
        if template_mgr.is_unified_format:
            # Use new unified template format (directly uses template strings)
            batch_prompt = template_mgr.build_batch_prompt_unified(
                contact_data=contact_data,
                use_cases_short=use_cases_short,
                use_cases_long=use_cases_long,
                value_prop_short=value_prop_short,
                value_prop_long=value_prop_long,
                company_name_short=company_name_short,
                # Deprecated variables (for backwards compatibility)
                use_cases_inline=use_cases_inline,
                use_cases_examples=use_cases_examples,
                value_prop_selection=value_prop_selection
            )
        else:
            # Use old component-based format (for backwards compatibility)
            # Get random CTAs and signatures from template
            cta_msg1 = template_mgr.get_random_cta(1)
            cta_msg2 = template_mgr.get_random_cta(2)
            cta_msg3 = template_mgr.get_random_cta(3)
            cta_msg4 = template_mgr.get_random_cta(4)
            signature_msg3 = template_mgr.get_random_signature(3)
            signature_msg4 = template_mgr.get_random_signature(4)

            # Build batch prompt using TemplateManager
            batch_prompt = template_mgr.build_batch_prompt(
                contact_data=contact_data,
                use_cases_inline=use_cases_inline,
                use_cases_examples=use_cases_examples,
                company_name_short=company_name_short,
                cta_msg1=cta_msg1,
                cta_msg2=cta_msg2,
                cta_msg3=cta_msg3,
                cta_msg4=cta_msg4,
                signature_msg3=signature_msg3,
                signature_msg4=signature_msg4
            )

        # Make ONE API call for all 4 messages (with retry for rate limits)
        # Route to appropriate LLM provider
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if self.llm_provider == "claude":
                    # Claude API call
                    message = self.client.messages.create(
                        model=self.model,
                        max_tokens=1800,
                        temperature=TEMPERATURE,
                        system=system_prompt_to_use,
                        messages=[{"role": "user", "content": batch_prompt}]
                    )
                    generated_text = message.content[0].text

                elif self.llm_provider == "openai":
                    # OpenAI API call
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": system_prompt_to_use},
                            {"role": "user", "content": batch_prompt}
                        ],
                        temperature=TEMPERATURE,
                        max_tokens=1800
                    )
                    generated_text = response.choices[0].message.content

                # Parse the 4 messages from response
                messages = self._parse_batch_response(generated_text, mode=mode)

                # Generate subject line if configured (email mode only)
                if mode == "email" and self.subject_line_config:
                    subject_line = self._generate_subject_line(
                        contact_data=contact_data,
                        first_message=messages.get('message_1', ''),
                        mode=mode
                    )
                    if subject_line:
                        messages['subject_line'] = subject_line

                return messages

            except (anthropic.RateLimitError, Exception) as e:
                # Handle rate limits for both providers
                if "rate" in str(e).lower() and attempt < max_retries - 1:
                    import time
                    import sys
                    wait_time = (attempt + 1) * 10  # 10, 20, 30 seconds
                    # Suppressed verbose rate limit logging - retrying silently
                    time.sleep(wait_time)
                    continue
                elif attempt == max_retries - 1:
                    return {f'message_{i}': f"ERROR: Rate limit exceeded ({self.llm_provider})" for i in range(1, 5)}
                else:
                    return {f'message_{i}': f"ERROR: {str(e)} ({self.llm_provider})" for i in range(1, 5)}

    def _get_subject_line_prompt(self, style: str, custom_prompt: Optional[str] = None) -> str:
        """
        Get the prompt instruction for subject line generation based on style.

        Args:
            style: "question", "direct", "curiosity", "value", or "custom"
            custom_prompt: Custom prompt for "custom" style

        Returns:
            Prompt instruction for subject line generation
        """
        style_prompts = {
            "question": "Generate a question-based subject line that piques curiosity and relates to their role/company. Example: 'Quick question about {company}'s fleet ops?'",
            "direct": "Generate a direct, straightforward subject line that clearly states the value proposition. Example: 'AI voice agents for {company}'s operations'",
            "curiosity": "Generate an intriguing subject line that creates curiosity without being clickbait. Example: 'Saw something interesting about {company}'",
            "value": "Generate a value-focused subject line that highlights a specific benefit. Example: 'Cut {company}'s call handling time by 60%'",
        }

        if style == "custom" and custom_prompt:
            return custom_prompt
        return style_prompts.get(style, style_prompts["question"])

    def _generate_subject_line(self, contact_data: Dict, first_message: str, mode: str) -> Optional[str]:
        """
        Generate a personalized subject line for the email.

        Args:
            contact_data: Contact information dict
            first_message: The generated first message (for context)
            mode: Message mode ("email" or "linkedin")

        Returns:
            Generated subject line or None if not email mode or no config
        """
        if mode != "email" or not self.subject_line_config:
            return None

        style = self.subject_line_config.get("style", "question")
        custom_prompt = self.subject_line_config.get("customPrompt")

        style_instruction = self._get_subject_line_prompt(style, custom_prompt)

        prompt = f"""Generate a single email subject line for this outreach.

RECIPIENT:
- Name: {contact_data['first_name']} {contact_data['last_name']}
- Title: {contact_data['title']}
- Company: {contact_data['company_name']}

STYLE INSTRUCTION:
{style_instruction}

CONTEXT (first message of the email sequence):
{first_message[:500]}...

RULES:
- Maximum 50 characters
- Do NOT use brackets or placeholders
- Use the actual company name (short form: {contact_data.get('company_name_for_emails', contact_data['company_name'])})
- Do NOT use ALL CAPS
- Do NOT use excessive punctuation (!!!)
- Make it feel personal and relevant to their role
- No salesy or spammy language

Output ONLY the subject line, nothing else."""

        try:
            if self.llm_provider == "claude":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=100,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                subject_line = response.content[0].text.strip()
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=100
                )
                subject_line = response.choices[0].message.content.strip()

            # Clean up the subject line (remove quotes if present)
            subject_line = subject_line.strip('"\'')

            # Ensure it's not too long
            if len(subject_line) > 60:
                subject_line = subject_line[:57] + "..."

            return subject_line

        except Exception as e:
            return f"ERROR: {str(e)}"

    def _format_value_props_conversational(self, value_props: List[str]) -> str:
        """
        Format value props conversationally with natural 'and' connector.
        Removes the clinical " / " separator in favor of natural language.

        Examples:
        - 1 prop: "scaling ops without adding headcount"
        - 2 props: "scaling ops without adding headcount and improving visibility"
        - 3 props: "scaling ops without adding headcount, improving visibility, and tightening handoffs"

        Args:
            value_props: List of value proposition strings

        Returns:
            Formatted string with natural connectors
        """
        if not value_props:
            return "operational efficiency"

        if len(value_props) == 1:
            return value_props[0]
        elif len(value_props) == 2:
            return f"{value_props[0]} and {value_props[1]}"
        else:
            # 3+ props: use commas with "and" before last
            return f"{', '.join(value_props[:-1])}, and {value_props[-1]}"

    def _format_email_html(self, text: str) -> str:
        """
        Convert plain text to HTML for maximum email client compatibility.

        Uses <br><br> between paragraphs instead of CSS margins because:
        - Works in ALL email clients (Outlook, Gmail, Apple Mail, etc.)
        - Survives Instantly.ai sanitization (no inline styles to strip)
        - Consistent across all templates and paste modes
        - Simple, bulletproof, and reliable

        This approach is recommended by email deliverability experts as the
        most robust way to handle paragraph spacing in HTML emails.
        """
        if not text or text.startswith("ERROR"):
            return text

        # Split by double line breaks (paragraphs)
        paragraphs = text.split('\n\n')

        # Process each paragraph
        formatted_paragraphs = []
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Replace single line breaks with <br> (for signatures, multi-line text)
            para = para.replace('\n', '<br>')

            formatted_paragraphs.append(para)

        # Join paragraphs with <br><br> (double line break = visual paragraph spacing)
        # This creates a blank line between paragraphs, which is universally supported
        return '<br><br>'.join(formatted_paragraphs)

    def _strip_message_identifiers(self, text: str) -> str:
        """
        Defensive function to strip message identifiers from generated text.
        Removes headers like "**MESSAGE 1:**", "MESSAGE 1:", etc.
        """
        import re

        # Strip common message identifier patterns at the start
        # Handles: **MESSAGE 1:**, MESSAGE 1:, **MESSAGE 1**, MESSAGE 1, etc.
        patterns = [
            r'^\*\*MESSAGE\s+\d+:?\*\*\s*',  # **MESSAGE 1:** or **MESSAGE 1**
            r'^MESSAGE\s+\d+:?\s*',           # MESSAGE 1: or MESSAGE 1
            r'^\*\*Message\s+\d+:?\*\*\s*',  # **Message 1:** (capitalization)
            r'^Message\s+\d+:?\s*',           # Message 1:
        ]

        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        return text.strip()

    def _normalize_dashes(self, text: str) -> str:
        """
        Defensive function to replace em dashes (—) and en dashes (–) with regular hyphens (-).
        Ensures consistent punctuation across all messages.
        """
        # Replace em dash (—) with regular hyphen with spaces
        text = text.replace('—', ' - ')
        # Replace en dash (–) with regular hyphen with spaces
        text = text.replace('–', ' - ')
        # Clean up any double spaces created
        text = text.replace('  ', ' ')
        return text

    def _normalize_newlines(self, text: str) -> str:
        """
        Defensive function to normalize excessive newlines.
        Reduces 3+ consecutive newlines down to 2 (double newline = single blank line).
        This prevents awkward extra spacing when LLMs add extra blank lines.
        """
        import re
        # Replace 3 or more newlines with exactly 2 newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text

    def _remove_forbidden_phrases(self, text: str) -> str:
        """
        Defensive function to remove/replace forbidden phrases from generated text.
        Particularly important for OpenAI which is less compliant with negative instructions.

        Forbidden phrases are defined in the system prompt but sometimes slip through,
        especially with OpenAI (60% violation rate for "impressive").
        """
        import re

        # Case-insensitive replacements for opinion-based language
        replacements = [
            # "impressive" -> remove or replace with neutral observation
            (r'\b([Ii])mpressive\b', r'\1nteresting'),
            (r'\bimpressively\b', 'notably'),

            # "no small feat" -> neutral alternative
            (r'\bno small feat\b', 'significant'),
            (r'\bNo small feat\b', 'Significant'),

            # "leverage" -> use simpler language
            (r'\bleverage\b', 'use'),
            (r'\bleveraging\b', 'using'),
            (r'\bLeverage\b', 'Use'),
            (r'\bLeveraging\b', 'Using'),

            # "recent/recently" -> be more specific or remove
            # Only replace when followed by generic words (not specific events)
            (r'\brecently\s+(posted|shared|moved|joined)\b', r'\1'),
            (r'\brecent\s+(post|move|role|position)\b', r'\1'),
        ]

        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text)

        return text

    def _parse_batch_response(self, generated_text: str, mode: str = "email") -> Dict[str, str]:
        """Parse the 4 messages from Claude's batch response"""

        # Split by message separators
        parts = generated_text.split("---MESSAGE ")

        messages = {}

        # Handle Message 1 - could be parts[0] OR parts with "1---" prefix
        if len(parts) > 0:
            if parts[0].strip() and not parts[0].strip().startswith("1---"):
                # Message 1 is before first separator
                msg1_text = parts[0].strip()
                # Defensive: Strip message identifiers, normalize dashes/newlines, remove forbidden phrases
                msg1_text = self._strip_message_identifiers(msg1_text)
                msg1_text = self._normalize_dashes(msg1_text)
                msg1_text = self._normalize_newlines(msg1_text)
                msg1_text = self._remove_forbidden_phrases(msg1_text)
                messages['message_1'] = msg1_text
            else:
                # Message 1 might have "---MESSAGE 1---" header
                for part in parts:
                    if part.startswith("1---"):
                        msg1_text = part[4:].strip()
                        msg1_text = self._strip_message_identifiers(msg1_text)
                        msg1_text = self._normalize_dashes(msg1_text)
                        msg1_text = self._normalize_newlines(msg1_text)
                        msg1_text = self._remove_forbidden_phrases(msg1_text)
                        messages['message_1'] = msg1_text
                        break

        # Parse Messages 2, 3, 4 (with defensive stripping, dash/newline normalization, and forbidden phrase cleanup)
        for i in range(1, len(parts)):
            if parts[i].startswith("2---"):
                msg_text = self._strip_message_identifiers(parts[i][4:].strip())
                msg_text = self._normalize_dashes(msg_text)
                msg_text = self._normalize_newlines(msg_text)
                msg_text = self._remove_forbidden_phrases(msg_text)
                messages['message_2'] = msg_text
            elif parts[i].startswith("3---"):
                msg_text = self._strip_message_identifiers(parts[i][4:].strip())
                msg_text = self._normalize_dashes(msg_text)
                msg_text = self._normalize_newlines(msg_text)
                msg_text = self._remove_forbidden_phrases(msg_text)
                messages['message_3'] = msg_text
            elif parts[i].startswith("4---"):
                msg_text = self._strip_message_identifiers(parts[i][4:].strip())
                msg_text = self._normalize_dashes(msg_text)
                msg_text = self._normalize_newlines(msg_text)
                msg_text = self._remove_forbidden_phrases(msg_text)
                messages['message_4'] = msg_text

        # Ensure all 4 messages exist
        for i in range(1, 5):
            key = f'message_{i}'
            if key not in messages or not messages[key]:
                messages[key] = f"ERROR: Message {i} not generated"

        # Format for email threading (Instantly.ai compatibility)
        # Only apply HTML formatting for email mode (LinkedIn respects plain text)
        if mode == "email":
            for key in messages:
                if not messages[key].startswith("ERROR"):
                    messages[key] = self._format_email_html(messages[key])

        return messages
