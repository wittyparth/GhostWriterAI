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
- Professional Title: {brand_profile.get('professional_title', 'Not specified')}
- Industry: {brand_profile.get('industry', 'Not specified')}
- Company: {brand_profile.get('company_name', 'Not specified')}

CONTENT STRATEGY:
- Content Pillars: {brand_profile.get('content_pillars', ['Not specified'])}
- Target Audience: {brand_profile.get('target_audience', 'Not specified')}
- Audience Pain Points: {brand_profile.get('audience_pain_points', [])}
- Expertise Areas: {brand_profile.get('expertise_areas', [])}

BRAND VOICE:
- Voice: {brand_profile.get('brand_voice', 'Not specified')}
- Writing Style: {brand_profile.get('writing_style', 'Not specified')}

PRIMARY GOAL: {brand_profile.get('primary_goal', 'thought_leadership')}
UNIQUE POSITIONING: {brand_profile.get('unique_positioning', 'Not specified')}

Evaluate if this idea:
1. Aligns with their content pillars and expertise
2. Addresses their target audience's pain points
3. Supports their primary goal
4. Can be written in their voice

Provide your evaluation as JSON."""
        
        result = await self.generate_structured(prompt)
        return ValidatorOutput(**result)

