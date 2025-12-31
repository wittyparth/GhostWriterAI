"""
Strategist Agent - Content strategy and format selection.

Generates clarifying questions, selects format, and determines structure.
"""

from typing import Any
from src.agents.base_agent import BaseAgent
from src.models.schemas import StrategistOutput, ClarifyingQuestion


class StrategistAgent(BaseAgent[StrategistOutput]):
    """Develops content strategy and generates clarifying questions."""
    
    agent_name = "strategist"
    
    @property
    def system_prompt(self) -> str:
        return """You are a LinkedIn content strategist.

Your job is to:
1. Select the best FORMAT (text, carousel, video script)
2. Choose a STRUCTURE pattern (story, list, framework, data, question)
3. Identify PSYCHOLOGICAL TRIGGERS to use
4. Generate 3-5 CLARIFYING QUESTIONS to gather more context

Respond in JSON:
{
  "recommended_format": "text|carousel|video",
  "format_reasoning": "Why this format works best",
  "structure_type": "story_post|list_post|framework_post|data_post|question_post",
  "hook_types": ["personal_story", "data_shock"],
  "psychological_triggers": ["curiosity_gap", "social_proof"],
  "tone": "conversational|authoritative|provocative",
  "clarifying_questions": [
    {"question_id": "q1", "question": "What specific outcome did you achieve?", "rationale": "Adds credibility", "required": true}
  ],
  "similar_posts": []
}"""
    
    async def _execute(self, input_data: dict[str, Any]) -> StrategistOutput:
        idea = input_data.get("raw_idea", "")
        brand_profile = input_data.get("brand_profile", {})
        validator_output = input_data.get("validator_output", {})
        
        prompt = f"""Develop a content strategy for this LinkedIn post idea:

IDEA: {idea}

BRAND PROFILE:
- Pillars: {brand_profile.get('content_pillars', [])}
- Audience: {brand_profile.get('target_audience', 'General professionals')}
- Voice: {brand_profile.get('brand_voice', 'Professional')}

VALIDATION NOTES: {validator_output.get('reasoning', 'Approved')}

Generate a strategy with format, structure, and 3-5 clarifying questions."""
        
        result = await self.generate_structured(prompt)
        return StrategistOutput(**result)
