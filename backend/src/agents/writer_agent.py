"""
Writer Agent - Content generation specialist.

Generates hooks, body content, and CTAs for LinkedIn posts.
"""

from typing import Any
from src.agents.base_agent import BaseAgent
from src.models.schemas import WriterOutput, HookVariation


class WriterAgent(BaseAgent[WriterOutput]):
    """Generates LinkedIn post content with multiple hook variations."""
    
    agent_name = "writer"
    
    @property
    def system_prompt(self) -> str:
        return """You are an expert LinkedIn content writer.

Your job is to create engaging posts that:
1. Generate 3 HOOK variations (score each 1-10)
2. Write the BODY content with proper formatting
3. Create a CTA that encourages engagement
4. Suggest relevant HASHTAGS (3-5)

FORMATTING RULES:
- Keep sentences short (under 12 words)
- Use line breaks for readability
- One idea per paragraph
- Use → ✓ • for visual breaks

Respond in JSON:
{
  "hooks": [
    {"version": 1, "text": "Hook text here", "hook_type": "personal_story", "score": 8.5, "reasoning": "Why this works"}
  ],
  "body_content": "The formatted body content with\\n\\nproper line breaks",
  "cta": "What's your experience with this?",
  "hashtags": ["leadership", "startup", "growthmindset"],
  "formatting_metadata": {"word_count": 150, "reading_time_seconds": 45}
}"""
    
    async def _execute(self, input_data: dict[str, Any]) -> WriterOutput:
        idea = input_data.get("raw_idea", "")
        strategy = input_data.get("strategy", {})
        user_answers = input_data.get("user_answers", {})
        brand_profile = input_data.get("brand_profile", {})
        
        # Build comprehensive brand context
        brand_context = f"""
BRAND VOICE: {brand_profile.get('brand_voice', 'Professional and authentic')}
WRITING STYLE: {brand_profile.get('writing_style', 'conversational')}
PERSONALITY TRAITS: {', '.join(brand_profile.get('personality_traits', []))}

AUTHOR CONTEXT:
- Title: {brand_profile.get('professional_title', 'Professional')}
- Industry: {brand_profile.get('industry', 'Business')}
- Experience: {brand_profile.get('years_of_experience', 'N/A')} years
- Company: {brand_profile.get('company_name', '')}

WORDS TO USE: {', '.join(brand_profile.get('words_to_use', []))}
WORDS TO AVOID: {', '.join(brand_profile.get('words_to_avoid', []))}

UNIQUE POSITIONING: {brand_profile.get('unique_positioning', '')}
UNIQUE PERSPECTIVE: {brand_profile.get('unique_perspective', '')}

ACHIEVEMENTS TO REFERENCE: {', '.join(brand_profile.get('achievements', []))}
PERSONAL EXPERIENCES: {', '.join(brand_profile.get('personal_experiences', []))}
""".strip()
        
        prompt = f"""Write a LinkedIn post based on:

IDEA: {idea}

STRATEGY:
- Format: {strategy.get('recommended_format', 'text')}
- Structure: {strategy.get('structure_type', 'story_post')}
- Tone: {strategy.get('tone', 'conversational')}
- Hook Types to Use: {strategy.get('hook_types', ['personal_story'])}
- Triggers: {strategy.get('psychological_triggers', ['curiosity_gap'])}

USER'S ADDITIONAL CONTEXT:
{user_answers}

{brand_context}

Generate 3 hook variations, body content, CTA, and hashtags.
The content should feel like it was written by this specific person with their unique voice."""
        
        result = await self.generate_structured(prompt)
        return WriterOutput(**result)
