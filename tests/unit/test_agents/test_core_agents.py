"""
Unit tests for agents.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.agents.validator_agent import ValidatorAgent
from src.agents.strategist_agent import StrategistAgent
from src.agents.writer_agent import WriterAgent


class TestValidatorAgent:
    """Tests for ValidatorAgent."""
    
    @pytest.fixture
    def agent(self):
        return ValidatorAgent()
    
    @pytest.mark.asyncio
    async def test_execute_approve(self, agent):
        """Test validator approves good idea."""
        mock_response = {
            "decision": "APPROVE",
            "quality_score": 8.5,
            "brand_alignment_score": 9.0,
            "reasoning": "Strong tactical value",
            "concerns": [],
            "refinement_suggestions": [],
        }
        
        with patch.object(agent, 'generate_structured', new_callable=AsyncMock) as mock:
            mock.return_value = mock_response
            
            result = await agent.execute({
                "raw_idea": "3 lessons from failing my startup",
                "brand_profile": {"content_pillars": ["startups"]},
            })
            
            assert result["status"] == "success"
            assert result["output"]["decision"] == "APPROVE"
            assert result["output"]["quality_score"] >= 7.0
    
    @pytest.mark.asyncio
    async def test_execute_reject(self, agent):
        """Test validator rejects low quality idea."""
        mock_response = {
            "decision": "REJECT",
            "quality_score": 3.0,
            "brand_alignment_score": 4.0,
            "reasoning": "Too generic",
            "concerns": ["Lacks specificity"],
            "refinement_suggestions": ["Add personal experience"],
        }
        
        with patch.object(agent, 'generate_structured', new_callable=AsyncMock) as mock:
            mock.return_value = mock_response
            
            result = await agent.execute({
                "raw_idea": "Success is good",
                "brand_profile": {},
            })
            
            assert result["status"] == "success"
            assert result["output"]["decision"] == "REJECT"


class TestStrategistAgent:
    """Tests for StrategistAgent."""
    
    @pytest.fixture
    def agent(self):
        return StrategistAgent()
    
    @pytest.mark.asyncio
    async def test_generates_questions(self, agent):
        """Test strategist generates clarifying questions."""
        mock_response = {
            "recommended_format": "text",
            "format_reasoning": "Personal story works best as text",
            "structure_type": "story_post",
            "hook_types": ["personal_story"],
            "psychological_triggers": ["curiosity_gap"],
            "tone": "conversational",
            "clarifying_questions": [
                {"question_id": "q1", "question": "What was your biggest lesson?", "rationale": "Adds depth", "required": True}
            ],
            "similar_posts": [],
        }
        
        with patch.object(agent, 'generate_structured', new_callable=AsyncMock) as mock:
            mock.return_value = mock_response
            
            result = await agent.execute({
                "raw_idea": "My startup journey",
                "brand_profile": {},
                "validator_output": {"decision": "APPROVE"},
            })
            
            assert result["status"] == "success"
            assert len(result["output"]["clarifying_questions"]) > 0


class TestWriterAgent:
    """Tests for WriterAgent."""
    
    @pytest.fixture
    def agent(self):
        return WriterAgent()
    
    @pytest.mark.asyncio
    async def test_generates_hooks(self, agent):
        """Test writer generates multiple hooks."""
        mock_response = {
            "hooks": [
                {"version": 1, "text": "I failed 3 times", "hook_type": "personal_story", "score": 8.5, "reasoning": "Strong opening"},
                {"version": 2, "text": "Most founders miss this", "hook_type": "curiosity", "score": 7.5, "reasoning": "Creates curiosity"},
                {"version": 3, "text": "Here's what nobody tells you", "hook_type": "contrarian", "score": 8.0, "reasoning": "Pattern interrupt"},
            ],
            "body_content": "Here's what I learned...",
            "cta": "What's your experience?",
            "hashtags": ["startup", "founders"],
            "formatting_metadata": {"word_count": 150},
        }
        
        with patch.object(agent, 'generate_structured', new_callable=AsyncMock) as mock:
            mock.return_value = mock_response
            
            result = await agent.execute({
                "raw_idea": "Startup lessons",
                "strategy": {"recommended_format": "text"},
                "user_answers": {},
                "brand_profile": {},
            })
            
            assert result["status"] == "success"
            assert len(result["output"]["hooks"]) == 3
            assert result["output"]["body_content"]
            assert result["output"]["cta"]
