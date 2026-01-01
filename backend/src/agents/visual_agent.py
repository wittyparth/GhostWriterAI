"""
Visual Specialist Agent - Carousel and image specifications.

Creates detailed visual specifications for carousel posts.
"""

from typing import Any
from src.agents.base_agent import BaseAgent
from src.models.schemas import VisualOutput, VisualSpecs, VisualSlide


class VisualAgent(BaseAgent[VisualOutput]):
    """Creates visual specifications for carousel and image posts."""
    
    agent_name = "visual"
    
    @property
    def system_prompt(self) -> str:
        return """You are a LinkedIn carousel design expert.

Your job is to create detailed visual specifications:
1. Plan 8-10 SLIDES for maximum engagement
2. Specify LAYOUT for each slide (title-only, title-body, image-text, etc.)
3. Write HEADLINES that are punchy (under 8 words)
4. Describe any IMAGES needed

Respond in JSON:
{
  "visual_specs": {
    "total_slides": 10,
    "slides": [
      {"slide_number": 1, "layout": "title_only", "headline": "Hook Slide Title", "body_text": null, "image_description": "Abstract geometric pattern", "design_notes": "Use brand colors"}
    ],
    "overall_style": "Modern minimalist with bold typography",
    "color_palette": ["#1E3A8A", "#FBBF24", "#FFFFFF"],
    "typography_notes": "Use Inter Bold for headlines"
  },
  "image_prompts": ["Generate abstract geometric pattern with blue and gold"]
}"""
    
    async def _execute(self, input_data: dict[str, Any]) -> VisualOutput:
        idea = input_data.get("raw_idea", "")
        writer_output = input_data.get("writer_output", {})
        brand_profile = input_data.get("brand_profile", {})
        
        prompt = f"""Create carousel visual specifications for:

IDEA: {idea}

CONTENT TO VISUALIZE:
{writer_output.get('body_content', '')}

BRAND GUIDELINES:
- Colors: {brand_profile.get('brand_colors', ['#1E3A8A', '#FBBF24'])}
- Visual Style: {brand_profile.get('visual_guidelines', {})}

Create 8-10 slide specifications with layouts, headlines, and image descriptions."""
        
        result = await self.generate_structured(prompt)
        return VisualOutput(**result)
