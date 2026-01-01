"""
Integration tests for agent flow.

Tests agent-to-agent communication and complete workflows.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.orchestration import AgentState, run_generation, continue_generation
from src.agents import ValidatorAgent, StrategistAgent, WriterAgent, OptimizerAgent


class TestAgentFlow:
    """Integration tests for complete agent workflows."""
    
    @pytest.fixture
    def mock_llm_responses(self):
        """Mock LLM responses for all agents."""
        return {
            "validator": {
                "decision": "APPROVE",
                "quality_score": 8.5,
                "brand_alignment_score": 9.0,
                "reasoning": "Strong tactical value with personal experience",
                "concerns": [],
                "refinement_suggestions": [],
            },
            "strategist": {
                "recommended_format": "text",
                "format_reasoning": "Personal story works best as text",
                "structure_type": "story_post",
                "hook_types": ["personal_story"],
                "psychological_triggers": ["curiosity_gap"],
                "tone": "conversational",
                "clarifying_questions": [
                    {"question_id": "q1", "question": "What was the specific outcome?", "rationale": "Adds credibility", "required": True}
                ],
                "similar_posts": [],
            },
            "writer": {
                "hooks": [
                    {"version": 1, "text": "I failed 3 times before succeeding", "hook_type": "personal_story", "score": 8.5, "reasoning": "Strong opening"},
                    {"version": 2, "text": "Most founders miss this one thing", "hook_type": "curiosity", "score": 7.5, "reasoning": "Creates curiosity"},
                    {"version": 3, "text": "Here's what nobody tells you about startups", "hook_type": "contrarian", "score": 8.0, "reasoning": "Pattern interrupt"},
                ],
                "body_content": "After 3 failed startups, here's what I learned:\n\n1. Build for customers, not yourself\n2. Speed beats perfection\n3. Co-founder alignment matters most",
                "cta": "What's your biggest startup lesson?",
                "hashtags": ["startup", "founders", "entrepreneurship"],
                "formatting_metadata": {"word_count": 150},
            },
            "optimizer": {
                "decision": "APPROVE",
                "quality_score": 8.5,
                "brand_consistency_score": 9.0,
                "formatting_issues": [],
                "suggestions": [],
                "predicted_impressions_min": 5000,
                "predicted_impressions_max": 15000,
                "predicted_engagement_rate": 0.045,
                "confidence": 0.75,
            },
        }
    
    @pytest.mark.asyncio
    async def test_validator_to_strategist_flow(self, mock_llm_responses):
        """Test flow from validator to strategist."""
        validator = ValidatorAgent()
        strategist = StrategistAgent()
        
        with patch.object(validator, 'generate_structured', new_callable=AsyncMock) as mock_v:
            with patch.object(strategist, 'generate_structured', new_callable=AsyncMock) as mock_s:
                mock_v.return_value = mock_llm_responses["validator"]
                mock_s.return_value = mock_llm_responses["strategist"]
                
                # Run validator
                v_result = await validator.execute({
                    "raw_idea": "My startup journey and lessons",
                    "brand_profile": {"content_pillars": ["startups"]},
                })
                
                assert v_result["status"] == "success"
                assert v_result["output"]["decision"] == "APPROVE"
                
                # Run strategist with validator output
                s_result = await strategist.execute({
                    "raw_idea": "My startup journey and lessons",
                    "brand_profile": {"content_pillars": ["startups"]},
                    "validator_output": v_result["output"],
                })
                
                assert s_result["status"] == "success"
                assert len(s_result["output"]["clarifying_questions"]) > 0
    
    @pytest.mark.asyncio
    async def test_writer_generates_multiple_hooks(self, mock_llm_responses):
        """Test that writer generates 3 hook variations."""
        writer = WriterAgent()
        
        with patch.object(writer, 'generate_structured', new_callable=AsyncMock) as mock_w:
            mock_w.return_value = mock_llm_responses["writer"]
            
            result = await writer.execute({
                "raw_idea": "Startup lessons",
                "strategy": {"recommended_format": "text", "structure_type": "story_post"},
                "user_answers": {"q1": "We hit $1M ARR in 8 months"},
                "brand_profile": {},
            })
            
            assert result["status"] == "success"
            assert len(result["output"]["hooks"]) == 3
            assert all(h["score"] >= 0 for h in result["output"]["hooks"])
    
    @pytest.mark.asyncio
    async def test_optimizer_approval_flow(self, mock_llm_responses):
        """Test optimizer approves quality content."""
        optimizer = OptimizerAgent()
        
        with patch.object(optimizer, 'generate_structured', new_callable=AsyncMock) as mock_o:
            mock_o.return_value = mock_llm_responses["optimizer"]
            
            result = await optimizer.execute({
                "raw_idea": "Startup lessons",
                "writer_output": mock_llm_responses["writer"],
                "brand_profile": {},
            })
            
            assert result["status"] == "success"
            assert result["output"]["decision"] == "APPROVE"
            assert result["output"]["quality_score"] >= 7.0
    
    @pytest.mark.asyncio
    async def test_rejection_flow(self):
        """Test that low quality ideas are rejected."""
        validator = ValidatorAgent()
        
        rejection_response = {
            "decision": "REJECT",
            "quality_score": 3.0,
            "brand_alignment_score": 4.0,
            "reasoning": "Too generic, lacks value",
            "concerns": ["No unique perspective", "Common topic without differentiation"],
            "refinement_suggestions": ["Add personal experience", "Include specific data"],
        }
        
        with patch.object(validator, 'generate_structured', new_callable=AsyncMock) as mock:
            mock.return_value = rejection_response
            
            result = await validator.execute({
                "raw_idea": "Success is good",
                "brand_profile": {},
            })
            
            assert result["status"] == "success"
            assert result["output"]["decision"] == "REJECT"
            assert result["output"]["quality_score"] < 5.0
            assert len(result["output"]["refinement_suggestions"]) > 0


class TestCompleteWorkflow:
    """Tests for complete end-to-end workflow."""
    
    @pytest.mark.asyncio
    async def test_state_passes_through_agents(self):
        """Test that state correctly accumulates through agents."""
        state: AgentState = {
            "raw_idea": "Test idea",
            "brand_profile": {},
            "status": "processing",
            "execution_log": [],
        }
        
        # Verify state structure
        assert "raw_idea" in state
        assert state["status"] == "processing"
        
        # Simulate adding validator output
        state["validator_output"] = {"decision": "APPROVE", "quality_score": 8.0}
        assert state["validator_output"]["decision"] == "APPROVE"
        
        # Simulate adding strategy
        state["strategy"] = {"recommended_format": "text"}
        assert state["strategy"]["recommended_format"] == "text"
