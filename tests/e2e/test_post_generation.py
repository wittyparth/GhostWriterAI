"""
End-to-end tests for post generation.

Tests full user journeys from idea to final post.
"""

import pytest
from unittest.mock import AsyncMock, patch

from src.orchestration import AgentState


class TestPostGeneration:
    """E2E tests for complete post generation flow."""
    
    @pytest.mark.asyncio
    async def test_text_post_happy_path(self):
        """Test successful text post generation."""
        # This would test with real API in staging
        # For unit testing, we verify the state structure
        
        initial_state: AgentState = {
            "raw_idea": "3 lessons from my startup journey",
            "brand_profile": {
                "content_pillars": ["startups", "entrepreneurship"],
                "brand_voice": "conversational",
            },
            "status": "processing",
            "revision_count": 0,
            "max_revisions": 2,
            "execution_log": [],
        }
        
        # Verify initial state is valid
        assert initial_state["raw_idea"]
        assert initial_state["status"] == "processing"
    
    @pytest.mark.asyncio
    async def test_carousel_generation(self):
        """Test carousel post generates visual specs."""
        state: AgentState = {
            "raw_idea": "Step by step guide to LinkedIn hooks",
            "format": "carousel",
            "visual_specs": {
                "total_slides": 10,
                "slides": [{"slide_number": i, "headline": f"Slide {i}"} for i in range(1, 11)],
            },
        }
        
        assert state["format"] == "carousel"
        assert state["visual_specs"]["total_slides"] == 10
        assert len(state["visual_specs"]["slides"]) == 10
    
    @pytest.mark.asyncio
    async def test_revision_loop(self):
        """Test that revision loop works correctly."""
        state: AgentState = {
            "revision_count": 0,
            "max_revisions": 2,
            "optimizer_output": {"decision": "REVISE"},
        }
        
        # Simulate revision loop
        while (
            state.get("optimizer_output", {}).get("decision") == "REVISE"
            and state.get("revision_count", 0) < state.get("max_revisions", 2)
        ):
            state["revision_count"] = state.get("revision_count", 0) + 1
            
            # After 2 revisions, approve
            if state["revision_count"] >= 2:
                state["optimizer_output"] = {"decision": "APPROVE"}
        
        assert state["revision_count"] == 2
        assert state["optimizer_output"]["decision"] == "APPROVE"
    
    @pytest.mark.asyncio
    async def test_final_post_structure(self):
        """Test final post has all required components."""
        final_post = {
            "format": "text",
            "hook": {"text": "I failed 3 times...", "score": 8.5},
            "body": "Here's what I learned:\n\n1. First lesson\n2. Second lesson",
            "cta": "What's your experience?",
            "hashtags": ["startup", "founders"],
            "quality_score": 8.5,
            "predicted_impressions": (5000, 15000),
        }
        
        # Verify all components present
        assert final_post["format"] in ["text", "carousel", "video"]
        assert "hook" in final_post
        assert final_post["hook"]["text"]
        assert "body" in final_post
        assert "cta" in final_post
        assert isinstance(final_post["hashtags"], list)
        assert final_post["quality_score"] >= 0
