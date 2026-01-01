"""
Validator Agent - Quality gate for incoming ideas.

Evaluates idea quality, brand alignment, and decides APPROVE/REFINE/REJECT.
"""

from typing import Any
from src.agents.base_agent import BaseAgent
from src.models.schemas import ValidatorOutput
from src.config.constants import MIN_QUALITY_SCORE_APPROVE, MIN_QUALITY_SCORE_REFINE


class ValidatorAgent(BaseAgent[ValidatorOutput]):
    """Validates ideas for quality and brand alignment."""
    
    agent_name = "validator"
    
    @property
    def system_prompt(self) -> str:
        return """You are a LinkedIn content expert who evaluates post ideas.

Your job is to assess:
1. QUALITY SCORE (1-10): How valuable, unique, and engaging is this idea?
2. BRAND ALIGNMENT (1-10): How well does it fit the user's content pillars?
3. DECISION: APPROVE (score >= 7), REFINE (5-6.9), or REJECT (< 5)

Be constructive. If rejecting or refining, provide specific suggestions.

Respond in JSON format:
{
  "decision": "APPROVE|REFINE|REJECT",
  "quality_score": 7.5,
  "brand_alignment_score": 8.0,
  "reasoning": "This idea has strong tactical value...",
  "concerns": ["May need more specificity"],
  "refinement_suggestions": ["Add a personal story element"]
}"""
    
    async def _execute(self, input_data: dict[str, Any]) -> ValidatorOutput:
        idea = input_data.get("raw_idea", "")
        brand_profile = input_data.get("brand_profile", {})
        
        prompt = f"""Evaluate this LinkedIn post idea:

IDEA: {idea}

USER'S BRAND PROFILE:
- Content Pillars: {brand_profile.get('content_pillars', ['Not specified'])}
- Target Audience: {brand_profile.get('target_audience', 'Not specified')}
- Brand Voice: {brand_profile.get('brand_voice', 'Not specified')}

Provide your evaluation as JSON."""
        
        result = await self.generate_structured(prompt)
        return ValidatorOutput(**result)
