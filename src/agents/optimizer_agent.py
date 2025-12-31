"""
Optimizer Agent - Quality assurance and performance prediction.

Validates formatting, scores brand consistency, and predicts performance.
"""

from typing import Any
from src.agents.base_agent import BaseAgent
from src.models.schemas import OptimizerOutput


class OptimizerAgent(BaseAgent[OptimizerOutput]):
    """Final QA, brand consistency scoring, and performance prediction."""
    
    agent_name = "optimizer"
    
    @property
    def system_prompt(self) -> str:
        return """You are a LinkedIn content quality analyst.

Your job is to:
1. CHECK formatting (line breaks, length, readability)
2. SCORE brand consistency (1-10)
3. PREDICT performance (impressions range, engagement rate)
4. SUGGEST improvements
5. Decide: APPROVE or REVISE

Respond in JSON:
{
  "decision": "APPROVE|REVISE",
  "quality_score": 8.5,
  "brand_consistency_score": 9.0,
  "formatting_issues": [],
  "suggestions": ["Consider adding a personal anecdote"],
  "predicted_impressions_min": 5000,
  "predicted_impressions_max": 15000,
  "predicted_engagement_rate": 0.045,
  "confidence": 0.7
}"""
    
    async def _execute(self, input_data: dict[str, Any]) -> OptimizerOutput:
        idea = input_data.get("raw_idea", "")
        writer_output = input_data.get("writer_output", {})
        brand_profile = input_data.get("brand_profile", {})
        
        hooks = writer_output.get("hooks", [])
        best_hook = hooks[0]["text"] if hooks else ""
        body = writer_output.get("body_content", "")
        cta = writer_output.get("cta", "")
        
        full_post = f"{best_hook}\n\n{body}\n\n{cta}"
        
        prompt = f"""Analyze this LinkedIn post for quality:

FULL POST:
{full_post}

BRAND PROFILE:
- Voice: {brand_profile.get('brand_voice', 'Professional')}
- Pillars: {brand_profile.get('content_pillars', [])}
- Audience: {brand_profile.get('target_audience', 'Professionals')}

Evaluate formatting, brand consistency, and predict performance."""
        
        result = await self.generate_structured(prompt)
        return OptimizerOutput(**result)
