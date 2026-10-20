"""
Template Manager
Loads, validates, and manages message templates from JSON files
"""

import json
import os
from typing import Dict, Any, List, Optional
import random


class TemplateManager:
    """
    Manages message templates for email and LinkedIn sequences
    Loads from JSON files and provides methods to build prompts
    """

    def __init__(self, mode: str = "linkedin", template_file: str = None, template_name: str = None):
        """
        Initialize template manager

        Args:
            mode: "email" or "linkedin" (DEPRECATED - only used for backwards compatibility)
            template_file: Optional custom template file path (takes precedence over template_name)
            template_name: Optional template name ("default_email" or "default_linkedin")
        """
        # Store mode for backwards compatibility (but it no longer controls template selection)
        self.mode = mode
        self.is_unified_format = False  # Track format type

        # Template selection logic (decoupled from mode):
        # 1. If custom template file path provided, use that
        # 2. If template name provided, use that
        # 3. Otherwise, fall back to old behavior for backwards compatibility
        if template_file:
            # Custom template file path provided
            self.template_path = template_file
        elif template_name:
            # Template name provided (new approach)
            templates_dir = os.path.join(os.path.dirname(__file__), "templates")
            self.template_path = os.path.join(templates_dir, f"{template_name}_template.json")
        else:
            # Backwards compatibility: fall back to mode-based selection
            templates_dir = os.path.join(os.path.dirname(__file__), "templates")
            # Try new default templates first, fall back to unified templates
            default_path = os.path.join(templates_dir, f"default_{mode}_template.json")
            unified_path = os.path.join(templates_dir, f"unified_{mode}_template.json")

            if os.path.exists(default_path):
                self.template_path = default_path
            else:
                self.template_path = unified_path

        # Load template
        self.template = self._load_template()

        # Store template's mode field for reference (informational only)
        self.template_mode = self.template.get("mode", mode)

    def _convert_unified_to_old_format(self, unified: Dict[str, Any]) -> Dict[str, Any]:
        """Convert unified template format to old format for backwards compatibility"""

        # Extract components from unified format
        msg1 = unified.get("message_1", {})
        msg2 = unified.get("message_2", {})
        msg3 = unified.get("message_3", {})
        msg4 = unified.get("message_4", {})

        # Build old format structure
        old_format = {
            "name": unified.get("name", "Converted Template"),
            "version": unified.get("version", "3.0"),
            "mode": unified.get("mode", "email"),
            "description": "Converted from unified format",

            # Simple components
            "greeting": "{first_name} -",
            "intro_line": "I'm with a company called Waypoint.",

            # Social proof from templates
            "social_proof": {
                "message_1": "We work with freight brokers, carriers, and shippers of every size, and have already automated millions of supply chain tasks.",
                "message_3": "We work with some of the largest freight brokers and carriers in North America. Most teams start with one high-volume phone or email workflow and expand from there."
            },

            "company_description": "We handle operational work for logistics companies - making calls, sending emails, updating systems, chasing docs. Things like {use_cases_inline}.",
            "product_description": "We built AI agents that sit on top of your existing systems - handling execution work (calls, emails, docs, systems) for things like {use_cases_examples}. ",

            "value_props": unified.get("value_props", [
                "scaling ops without adding headcount",
                "real-time visibility without manual check-calls",
                "tighter handoffs between teams",
                "better customer experience as volume grows"
            ]),

            # Convert message structures
            "message_1": {
                "personalization_instructions": msg1.get("personalization_instruction", "Natural, conversational personalization about their work"),
            },
            "message_2": {
                "opening": "Hey {first_name} - bumping this up in case it got lost.",
                "personalization_instructions": msg2.get("personalization_instruction", "One natural sentence tying to their work"),
                "signature": ""
            },
            "message_3": {
                "personalization_instructions": msg3.get("personalization_instruction", "One conversational sentence about their role"),
            },
            "message_4": {
                "opening": "{first_name},",
                "personalization_instructions": msg4.get("personalization_instruction", "1-2 thoughtful sentences about their situation"),
                "graceful_exit_instructions": msg4.get("graceful_exit_instruction", "Graceful exit referencing something from their research"),
                "acknowledgment_options": msg4.get("acknowledgment_options", ["Last note from me.", "I'll leave it here."])
            },

            # CTAs and signatures
            "cta_options": {
                "message_1": msg1.get("cta_options", []),
                "message_2": msg2.get("cta_options", []),
                "message_3": msg3.get("cta_options", []),
                "message_4": msg4.get("cta_options", [])
            },
            "signature_options": {
                "message_3": msg3.get("signature_options", ["Best,\nZarek Livak"]),
                "message_4": msg4.get("signature_options", ["Best,\nZarek Livak"])
            }
        }

        return old_format

    def _load_template(self) -> Dict[str, Any]:
        """Load template from JSON file"""
        try:
            with open(self.template_path, 'r') as f:
                template = json.load(f)

            # Check if this is NEW unified format or OLD format
            if "system_prompt" in template:
                # NEW unified format - keep it as-is and set flag
                required_fields = ["name", "mode", "system_prompt", "message_1", "message_2", "message_3", "message_4"]
                missing = [f for f in required_fields if f not in template]
                if missing:
                    raise ValueError(f"Unified template missing required fields: {missing}")

                self.is_unified_format = True
                return template
            else:
                # OLD format validation (for backwards compatibility)
                required_fields = ["name", "mode", "greeting", "intro_line", "social_proof"]
                missing = [f for f in required_fields if f not in template]
                if missing:
                    raise ValueError(f"Template missing required fields: {missing}")

                self.is_unified_format = False
                return template
        except FileNotFoundError:
            raise FileNotFoundError(f"Template file not found: {self.template_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in template file: {e}")

    def get_greeting(self, first_name: str) -> str:
        """Get formatted greeting"""
        return self.template["greeting"].format(first_name=first_name)

    def get_intro_line(self) -> str:
        """Get intro line"""
        return self.template["intro_line"]

    def get_social_proof(self, message_num: int) -> str:
        """Get social proof for specific message"""
        sp = self.template["social_proof"]
        if isinstance(sp, dict):
            return sp.get(f"message_{message_num}", sp["message_1"])
        return sp

    def get_company_description(self, use_cases_inline: str) -> str:
        """Get company description with use cases"""
        return self.template["company_description"].format(use_cases_inline=use_cases_inline)

    def get_product_description(self, use_cases_examples: str) -> str:
        """Get product description with use cases"""
        return self.template["product_description"].format(use_cases_examples=use_cases_examples)

    def get_random_cta(self, message_num: int) -> str:
        """Get random CTA for specified message"""
        # Handle both old format (cta_options at root) and unified format (in message)
        if "cta_options" in self.template:
            # Old format
            ctas = self.template["cta_options"].get(f"message_{message_num}", [])
        else:
            # Unified format - get from message directly
            msg_key = f"message_{message_num}"
            ctas = self.template.get(msg_key, {}).get("cta_options", [])

        return random.choice(ctas) if ctas else ""

    def get_random_signature(self, message_num: int) -> str:
        """Get random signature for specified message"""
        # Handle both old format (signature_options at root) and unified format (in message)
        if "signature_options" in self.template:
            # Old format
            sigs = self.template["signature_options"].get(f"message_{message_num}", [])
        else:
            # Unified format - get from message directly
            msg_key = f"message_{message_num}"
            sigs = self.template.get(msg_key, {}).get("signature_options", [])

        return random.choice(sigs) if sigs else ""

    def get_random_acknowledgment(self) -> str:
        """Get random message 4 acknowledgment"""
        acks = self.template["message_4"].get("acknowledgment_options", [])
        return random.choice(acks) if acks else "Last note from me."

    def get_message_2_opening(self, first_name: str) -> str:
        """Get Message 2 opening"""
        return self.template["message_2"]["opening"].format(first_name=first_name)

    def get_message_4_opening(self, first_name: str) -> str:
        """Get Message 4 opening"""
        return self.template["message_4"]["opening"].format(first_name=first_name)

    def get_value_props(self, count: int = 2) -> List[str]:
        """Get random selection of value props"""
        props = self.template["value_props"]
        return random.sample(props, min(count, len(props)))

    def build_batch_prompt(
        self,
        contact_data: Dict[str, Any],
        use_cases_inline: str,
        use_cases_examples: str,
        company_name_short: str,
        cta_msg1: str,
        cta_msg2: str,
        cta_msg3: str,
        cta_msg4: str,
        signature_msg3: str,
        signature_msg4: str
    ) -> str:
        """
        Build complete batch prompt for all 4 messages

        Args:
            contact_data: Contact information dictionary
            use_cases_inline: Inline use cases for message 1
            use_cases_examples: Example use cases for message 3
            company_name_short: Shortened company name
            cta_msg1: CTA for message 1
            cta_msg2: CTA for message 2
            cta_msg3: CTA for message 3
            cta_msg4: CTA for message 4
            signature_msg3: Signature for message 3
            signature_msg4: Signature for message 4

        Returns:
            Complete prompt string
        """

        # Get template components
        greeting = self.get_greeting(contact_data['first_name'])
        intro_line = self.get_intro_line()
        social_proof_msg1 = self.get_social_proof(1)
        social_proof_msg3 = self.get_social_proof(3)
        company_desc = self.get_company_description(use_cases_inline)
        product_desc = self.get_product_description(use_cases_examples)
        msg2_opening = self.get_message_2_opening(contact_data['first_name'])
        msg4_opening = self.get_message_4_opening(contact_data['first_name'])

        # Get personalization instructions
        msg1_pers_inst = self.template["message_1"]["personalization_instructions"]
        msg2_pers_inst = self.template["message_2"]["personalization_instructions"]
        msg3_pers_inst = self.template["message_3"]["personalization_instructions"]
        msg4_pers_inst = self.template["message_4"]["personalization_instructions"]
        msg4_exit_inst = self.template["message_4"]["graceful_exit_instructions"]

        # Get critical instructions
        critical_inst = self.template.get("critical_instructions", [])

        # Get personalization style guide
        style_guide = self.template.get("personalization_style_guide", {})
        good_examples = style_guide.get("good_examples", [])
        avoid = style_guide.get("avoid", [])

        # Message 2 signature
        msg2_sig = self.template["message_2"].get("signature", "")

        # Build prompt
        prompt = f"""Generate a complete 4-message {self.template_mode} sequence for {contact_data['first_name']} {contact_data['last_name']}.

**Contact Info:**
- Name: {contact_data['first_name']} {contact_data['last_name']}
- Title: {contact_data['title']}
- Company (full name): {contact_data['company_name']}
- Company (short name for messages): {company_name_short}

IMPORTANT: When mentioning the company in messages, ALWAYS use the SHORT NAME "{company_name_short}" - never the full legal name.

**Research:**
Personal: {contact_data['personal_research'][:800]}
Company: {contact_data['company_research'][:800]}

**ANTI-HALLUCINATION RULES (MANDATORY):**
- ONLY reference information EXPLICITLY stated in the Personal or Company research above
- If the Personal research is empty, generic, or not useful, use Company research instead
- NEVER invent, assume, or hallucinate posts, quotes, statements, or achievements the contact may have made
- NEVER reference "your post about X" or "your thoughts on X" unless that EXACT topic appears in the research
- If no specific personal information exists, focus on their ROLE and COMPANY context instead
- When in doubt, be vague rather than specific (e.g., "your work at [Company]" instead of inventing a topic)

**PERSONALIZATION STRATEGY (IMPORTANT):**
There are TWO types of personalization - handle them differently:

1. **OPERATIONALLY RELEVANT details** (posts about automation, efficiency, scaling challenges, AI, operational pain points, logistics/supply chain issues):
   - These ARE worth weaving throughout the sequence as a narrative thread
   - Build a cohesive story: introduce in Msg1, reference back in Msg3 ("given what you mentioned about..."), tie together in Msg4
   - This creates a compelling, connected outreach that shows you understand their challenges

2. **TANGENTIAL/PERSONAL details** (book clubs, marathons, team visits, leadership philosophy, personal achievements):
   - Mention ONCE (usually in Msg1) then VARY - use different details or role/company context for other messages
   - Do NOT hammer the same personal fact repeatedly - it feels try-hard and disconnected from the pitch
   - If research only has tangential details, reference one in Msg1, then pivot to role/company context for Msg3 and Msg4

The key question: Does this detail connect to operational challenges Waypoint solves? If YES, weave it. If NO, mention once and move on.

**CRITICAL INSTRUCTIONS:**
"""

        for inst in critical_inst:
            prompt += f"- {inst}\n"

        prompt += f"""
**PERSONALIZATION STYLE GUIDE:**
Good examples:
"""
        for ex in good_examples:
            prompt += f"- \"{ex}\"\n"

        prompt += "\nAvoid:\n"
        for av in avoid:
            prompt += f"- {av}\n"

        prompt += f"""
**MESSAGE 1 STRUCTURE:**
{greeting}

[{msg1_pers_inst}]

{intro_line} {company_desc}

{social_proof_msg1}

{cta_msg1}

Best,
Zarek Livak

**MESSAGE 2 STRUCTURE:**
{msg2_opening}

[{msg2_pers_inst}]. {cta_msg2}.

{msg2_sig}

**MESSAGE 3 STRUCTURE:**
{contact_data['first_name']} - [{msg3_pers_inst}]

{social_proof_msg3}

{product_desc}

For companies like {company_name_short}, that means [1-2 outcomes: {' / '.join(self.get_value_props(4))}].

{cta_msg3}

{signature_msg3}

**MESSAGE 4 STRUCTURE:**
{msg4_opening}

[REQUIRED: Warm, human acknowledgment this is last message - 1 sentence. Examples: "Last note from me - I know your inbox is packed." or "I'll leave it here after this one." Keep it natural.]

[{msg4_pers_inst}]

{cta_msg4}

[{msg4_exit_inst}]

{signature_msg4}

Generate all 4 messages now. Use exactly "---MESSAGE 2---", "---MESSAGE 3---", "---MESSAGE 4---" as separators."""

        return prompt

    def build_batch_prompt_unified(
        self,
        contact_data: Dict[str, Any],
        company_name_short: str,
        use_cases_short: Optional[str] = None,
        use_cases_long: Optional[str] = None,
        value_prop_short: Optional[str] = None,
        value_prop_long: Optional[str] = None,
        # Deprecated parameters (for backwards compatibility)
        use_cases_inline: Optional[str] = None,
        use_cases_examples: Optional[str] = None,
        value_prop_selection: Optional[str] = None
    ) -> str:
        """
        Build complete batch prompt using UNIFIED template format
        This directly uses the template strings from the unified format

        Args:
            contact_data: Contact information dictionary
            company_name_short: Shortened company name
            use_cases_short: SHORT version (2 use cases) for lighter messages
            use_cases_long: LONG version (4 use cases) for comprehensive messages
            value_prop_short: SHORT version (1 value prop) for concise messaging
            value_prop_long: LONG version (3 value props) for detailed messaging
            use_cases_inline: DEPRECATED - use use_cases_long instead
            use_cases_examples: DEPRECATED - kept for backwards compatibility
            value_prop_selection: DEPRECATED - use value_prop_long instead

        Returns:
            Complete prompt string
        """

        # Backwards compatibility: if old variables passed but new ones not, map them
        if use_cases_short is None and use_cases_inline:
            use_cases_short = use_cases_inline  # Fallback
            use_cases_long = use_cases_inline
        if value_prop_short is None and value_prop_selection:
            value_prop_short = value_prop_selection  # Fallback
            value_prop_long = value_prop_selection

        # Get message templates
        msg1 = self.template.get("message_1", {})
        msg2 = self.template.get("message_2", {})
        msg3 = self.template.get("message_3", {})
        msg4 = self.template.get("message_4", {})

        # Get random CTAs
        cta_msg1 = random.choice(msg1.get("cta_options", [""])) if msg1.get("cta_options") else ""
        cta_msg2 = random.choice(msg2.get("cta_options", [""])) if msg2.get("cta_options") else ""
        cta_msg3 = random.choice(msg3.get("cta_options", [""])) if msg3.get("cta_options") else ""
        cta_msg4 = random.choice(msg4.get("cta_options", [""])) if msg4.get("cta_options") else ""

        # Get random signatures for ALL messages
        sig_msg1 = random.choice(msg1.get("signature_options", [])) if msg1.get("signature_options") else ""
        sig_msg2 = random.choice(msg2.get("signature_options", [])) if msg2.get("signature_options") else ""
        sig_msg3 = random.choice(msg3.get("signature_options", [])) if msg3.get("signature_options") else ""
        sig_msg4 = random.choice(msg4.get("signature_options", [])) if msg4.get("signature_options") else ""

        # Get random acknowledgment for message 4
        ack_msg4 = random.choice(msg4.get("acknowledgment_options", ["Last note from me."])) if msg4.get("acknowledgment_options") else "Last note from me."

        # Get value props for message 3 - use override if provided, otherwise use template
        if value_prop_selection:
            value_prop_text = value_prop_selection
        else:
            value_props = self.template.get("value_props", [])
            selected_props = random.sample(value_props, min(3, len(value_props))) if value_props else []
            value_prop_text = " / ".join(selected_props) if selected_props else "operational efficiency and better visibility"

        # Build prompt using unified template
        # NOTE: We don't use system_prompt here because it's passed separately in batch_message_generator.py
        prompt = f"""Generate a complete 4-message {self.template_mode} sequence for {contact_data['first_name']} {contact_data['last_name']}.

**Contact Info:**
- Name: {contact_data['first_name']} {contact_data['last_name']}
- Title: {contact_data['title']}
- Company (full name): {contact_data['company_name']}
- Company (short name for messages): {company_name_short}

IMPORTANT: When mentioning the company in messages, ALWAYS use the SHORT NAME "{company_name_short}" - never the full legal name.

**Research:**
Personal: {contact_data['personal_research'][:800]}
Company: {contact_data['company_research'][:800]}

**ANTI-HALLUCINATION RULES (MANDATORY):**
- ONLY reference information EXPLICITLY stated in the Personal or Company research above
- If the Personal research is empty, generic, or not useful, use Company research instead
- NEVER invent, assume, or hallucinate posts, quotes, statements, or achievements the contact may have made
- NEVER reference "your post about X" or "your thoughts on X" unless that EXACT topic appears in the research
- If no specific personal information exists, focus on their ROLE and COMPANY context instead
- When in doubt, be vague rather than specific (e.g., "your work at [Company]" instead of inventing a topic)

**PERSONALIZATION STRATEGY (IMPORTANT):**
There are TWO types of personalization - handle them differently:

1. **OPERATIONALLY RELEVANT details** (posts about automation, efficiency, scaling challenges, AI, operational pain points, logistics/supply chain issues):
   - These ARE worth weaving throughout the sequence as a narrative thread
   - Build a cohesive story: introduce in Msg1, reference back in Msg3 ("given what you mentioned about..."), tie together in Msg4
   - This creates a compelling, connected outreach that shows you understand their challenges

2. **TANGENTIAL/PERSONAL details** (book clubs, marathons, team visits, leadership philosophy, personal achievements):
   - Mention ONCE (usually in Msg1) then VARY - use different details or role/company context for other messages
   - Do NOT hammer the same personal fact repeatedly - it feels try-hard and disconnected from the pitch
   - If research only has tangential details, reference one in Msg1, then pivot to role/company context for Msg3 and Msg4

The key question: Does this detail connect to operational challenges Waypoint solves? If YES, weave it. If NO, mention once and move on.

**CRITICAL INSTRUCTIONS:**
"""

        # Add critical instructions if provided
        for inst in self.template.get("critical_instructions", []):
            prompt += f"- {inst}\n"

        # Add personalization style guide if provided
        style_guide = self.template.get("personalization_style_guide", {})
        if style_guide:
            prompt += "\n**PERSONALIZATION STYLE GUIDE:**\n"
            if style_guide.get("good_examples"):
                prompt += "Good examples:\n"
                for ex in style_guide["good_examples"]:
                    prompt += f"- \"{ex}\"\n"
            if style_guide.get("avoid"):
                prompt += "\nAvoid:\n"
                for av in style_guide["avoid"]:
                    prompt += f"- {av}\n"

        # Message 1 (no header - starts immediately, parsed as content before first ---MESSAGE N--- separator)
        msg1_template = msg1.get("template", "")
        # Replace placeholders - NEW variables (short/long)
        msg1_filled = msg1_template.replace("{first_name}", contact_data['first_name'])
        # Support both {company_name_short} and {company_name_for_emails} for clarity
        msg1_filled = msg1_filled.replace("{company_name_short}", company_name_short)
        msg1_filled = msg1_filled.replace("{company_name_for_emails}", company_name_short)
        msg1_filled = msg1_filled.replace("{use_cases_short}", use_cases_short or "")
        msg1_filled = msg1_filled.replace("{use_cases_long}", use_cases_long or "")
        msg1_filled = msg1_filled.replace("{value_prop_short}", value_prop_short or "")
        msg1_filled = msg1_filled.replace("{value_prop_long}", value_prop_long or "")
        # DEPRECATED variables (backwards compatibility)
        msg1_filled = msg1_filled.replace("{use_cases_inline}", use_cases_inline or use_cases_long or "")
        msg1_filled = msg1_filled.replace("{use_cases_examples}", use_cases_examples or "")
        msg1_filled = msg1_filled.replace("{value_prop_selection}", value_prop_selection or value_prop_long or "")
        msg1_filled = msg1_filled.replace("{cta}", cta_msg1)
        msg1_filled = msg1_filled.replace("{signature}", sig_msg1)

        # Check if template has personalization placeholders
        has_pers1 = "{personalization}" in msg1_filled
        has_pers2 = "{personalization2}" in msg1_filled

        if has_pers1 or has_pers2:
            # Template has placeholders - show personalization instructions AND enforce exact structure
            placeholders = []
            if has_pers1:
                placeholders.append("{personalization}")
            if has_pers2:
                placeholders.append("{personalization2}")

            placeholders_str = " and ".join(placeholders)
            prompt += f"\nCRITICAL: Use the EXACT template structure below. Replace ONLY the {placeholders_str} placeholder(s) with the personalization content described. Do NOT change any other text, greetings, or structure.\n\n"

            if has_pers1 and msg1.get("personalization_instruction"):
                prompt += f"[Personalization to insert: {msg1['personalization_instruction']}]\n\n"
            if has_pers2 and msg1.get("personalization_instruction_2"):
                prompt += f"[Personalization 2 to insert: {msg1['personalization_instruction_2']}]\n\n"

            prompt += f"EXACT TEMPLATE TO USE:\n{msg1_filled}\n"
        else:
            # Template is complete - use it verbatim WITHOUT modification
            prompt += f"\nCRITICAL: Output ONLY the exact text below with NO headers, NO labels like 'MESSAGE 1:', NO markdown formatting indicators, and NO other modifications. Begin your response with the FIRST WORD of this text:\n\n{msg1_filled}\n"

        prompt += "\n---MESSAGE 2---\n"
        # Message 2
        msg2_template = msg2.get("template", "")
        msg2_filled = msg2_template.replace("{first_name}", contact_data['first_name'])
        # Support both {company_name_short} and {company_name_for_emails} for clarity
        msg2_filled = msg2_filled.replace("{company_name_short}", company_name_short)
        msg2_filled = msg2_filled.replace("{company_name_for_emails}", company_name_short)
        msg2_filled = msg2_filled.replace("{cta}", cta_msg2)
        msg2_filled = msg2_filled.replace("{signature}", sig_msg2)

        # Check if template has personalization placeholders
        has_pers1 = "{personalization}" in msg2_filled
        has_pers2 = "{personalization2}" in msg2_filled

        if has_pers1 or has_pers2:
            # Template has placeholders - show personalization instructions AND enforce exact structure
            placeholders = []
            if has_pers1:
                placeholders.append("{personalization}")
            if has_pers2:
                placeholders.append("{personalization2}")

            placeholders_str = " and ".join(placeholders)
            prompt += f"CRITICAL: Use the EXACT template structure below. Replace ONLY the {placeholders_str} placeholder(s) with the personalization content described. Do NOT change any other text, greetings, or structure.\n\n"

            if has_pers1 and msg2.get("personalization_instruction"):
                prompt += f"[Personalization to insert: {msg2['personalization_instruction']}]\n\n"
            if has_pers2 and msg2.get("personalization_instruction_2"):
                prompt += f"[Personalization 2 to insert: {msg2['personalization_instruction_2']}]\n\n"

            prompt += f"EXACT TEMPLATE TO USE:\n{msg2_filled}\n"
        else:
            # Template is complete - use it verbatim WITHOUT modification
            prompt += f"CRITICAL: Output ONLY this exact text with NO labels like 'MESSAGE 2:', NO headers, and NO modifications:\n\n{msg2_filled}\n"

        prompt += "\n---MESSAGE 3---\n"
        # Message 3
        msg3_template = msg3.get("template", "")
        msg3_filled = msg3_template.replace("{first_name}", contact_data['first_name'])
        # Support both {company_name_short} and {company_name_for_emails} for clarity
        msg3_filled = msg3_filled.replace("{company_name_short}", company_name_short)
        msg3_filled = msg3_filled.replace("{company_name_for_emails}", company_name_short)
        # NEW variables (short/long)
        msg3_filled = msg3_filled.replace("{use_cases_short}", use_cases_short or "")
        msg3_filled = msg3_filled.replace("{use_cases_long}", use_cases_long or "")
        msg3_filled = msg3_filled.replace("{value_prop_short}", value_prop_short or "")
        msg3_filled = msg3_filled.replace("{value_prop_long}", value_prop_long or "")
        # DEPRECATED variables (backwards compatibility)
        msg3_filled = msg3_filled.replace("{use_cases_examples}", use_cases_examples or use_cases_long or "")
        msg3_filled = msg3_filled.replace("{value_prop_selection}", value_prop_text)
        msg3_filled = msg3_filled.replace("{cta}", cta_msg3)
        msg3_filled = msg3_filled.replace("{signature}", sig_msg3)

        # Check if template has personalization placeholders
        has_pers1 = "{personalization}" in msg3_filled
        has_pers2 = "{personalization2}" in msg3_filled

        if has_pers1 or has_pers2:
            # Template has placeholders - show personalization instructions AND enforce exact structure
            placeholders = []
            if has_pers1:
                placeholders.append("{personalization}")
            if has_pers2:
                placeholders.append("{personalization2}")

            placeholders_str = " and ".join(placeholders)
            prompt += f"CRITICAL: Use the EXACT template structure below. Replace ONLY the {placeholders_str} placeholder(s) with the personalization content described. Do NOT change any other text, greetings, or structure.\n\n"

            if has_pers1 and msg3.get("personalization_instruction"):
                prompt += f"[Personalization to insert: {msg3['personalization_instruction']}]\n\n"
            if has_pers2 and msg3.get("personalization_instruction_2"):
                prompt += f"[Personalization 2 to insert: {msg3['personalization_instruction_2']}]\n\n"

            prompt += f"EXACT TEMPLATE TO USE:\n{msg3_filled}\n"
        else:
            # Template is complete - use it verbatim WITHOUT modification
            prompt += f"CRITICAL: Output ONLY this exact text with NO labels like 'MESSAGE 3:', NO headers, and NO modifications:\n\n{msg3_filled}\n"

        prompt += "\n---MESSAGE 4---\n"
        # Message 4
        msg4_template = msg4.get("template", "")
        msg4_filled = msg4_template.replace("{first_name}", contact_data['first_name'])
        # Support both {company_name_short} and {company_name_for_emails} for clarity
        msg4_filled = msg4_filled.replace("{company_name_short}", company_name_short)
        msg4_filled = msg4_filled.replace("{company_name_for_emails}", company_name_short)
        msg4_filled = msg4_filled.replace("{acknowledgment}", ack_msg4)
        msg4_filled = msg4_filled.replace("{cta}", cta_msg4)
        msg4_filled = msg4_filled.replace("{signature}", sig_msg4)

        # Check if template has personalization placeholders
        has_pers1 = "{personalization}" in msg4_filled
        has_pers2 = "{personalization2}" in msg4_filled
        has_graceful = "{graceful_exit}" in msg4_filled

        if has_pers1 or has_pers2 or has_graceful:
            # Template has placeholders - show instructions AND enforce exact structure
            placeholders = []
            if has_pers1:
                placeholders.append("{personalization}")
            if has_pers2:
                placeholders.append("{personalization2}")
            if has_graceful:
                placeholders.append("{graceful_exit}")

            placeholders_str = ", ".join(placeholders[:-1]) + (" and " + placeholders[-1] if len(placeholders) > 1 else placeholders[0] if placeholders else "")
            prompt += f"CRITICAL: Use the EXACT template structure below. Replace ONLY the {placeholders_str} placeholder(s) with the content described. Do NOT change any other text, greetings, or structure.\n\n"

            if has_pers1 and msg4.get("personalization_instruction"):
                prompt += f"[Personalization to insert: {msg4['personalization_instruction']}]\n\n"
            if has_pers2 and msg4.get("personalization_instruction_2"):
                prompt += f"[Personalization 2 to insert: {msg4['personalization_instruction_2']}]\n\n"
            if has_graceful and msg4.get("graceful_exit_instruction"):
                prompt += f"[Graceful exit to insert: {msg4['graceful_exit_instruction']}]\n\n"

            prompt += f"EXACT TEMPLATE TO USE:\n{msg4_filled}\n"
        else:
            # Template is complete - use it verbatim WITHOUT modification
            prompt += f"CRITICAL: Output ONLY this exact text with NO labels like 'MESSAGE 4:', NO headers, and NO modifications:\n\n{msg4_filled}\n"

        prompt += '\nGenerate all 4 messages now. Use exactly "---MESSAGE 2---", "---MESSAGE 3---", "---MESSAGE 4---" as separators.'

        return prompt

    def save_template(self, filepath: str = None):
        """Save current template to file"""
        save_path = filepath or self.template_path
        with open(save_path, 'w') as f:
            json.dump(self.template, f, indent=2)

    def get_system_prompt(self) -> str:
        """Get system prompt (for unified templates) or None"""
        if self.is_unified_format:
            return self.template.get("system_prompt", None)
        return None

    def get_template_info(self) -> Dict[str, Any]:
        """Get template metadata"""
        return {
            "name": self.template.get("name"),
            "version": self.template.get("version"),
            "mode": self.template.get("mode"),
            "description": self.template.get("description")
        }
