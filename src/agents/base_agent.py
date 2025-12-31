"""
Base Agent class for all LinkedIn content agents.

Provides common functionality for LLM interaction, error handling, and logging.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic

from pydantic import BaseModel

from src.llm.gemini import GeminiClient, GeminiModel, get_gemini_client
from src.config.settings import get_settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class BaseAgent(ABC, Generic[T]):
    """
    Abstract base class for all agents.
    
    Provides:
    - LLM client access
    - Structured output generation
    - Execution timing and logging
    - Error handling with retries
    """
    
    agent_name: str = "base"
    default_model: GeminiModel = GeminiModel.GEMINI_3_FLASH
    
    def __init__(self, llm_client: GeminiClient | None = None):
        self.llm = llm_client or get_gemini_client()
        self.settings = get_settings()
    
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass
    
    @abstractmethod
    async def _execute(self, input_data: dict[str, Any]) -> T:
        """Execute the agent logic. Override in subclasses."""
        pass
    
    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the agent with timing and error handling.
        
        Returns dict with output and metadata.
        """
        start_time = time.time()
        
        try:
            result = await self._execute(input_data)
            execution_time = int((time.time() - start_time) * 1000)
            
            logger.info(f"{self.agent_name} completed in {execution_time}ms")
            
            return {
                "output": result.model_dump() if isinstance(result, BaseModel) else result,
                "agent": self.agent_name,
                "execution_time_ms": execution_time,
                "status": "success",
            }
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"{self.agent_name} failed: {e}")
            
            return {
                "output": None,
                "agent": self.agent_name,
                "execution_time_ms": execution_time,
                "status": "error",
                "error": str(e),
            }
    
    async def generate_structured(
        self,
        prompt: str,
        output_schema: dict[str, Any] | None = None,
        model: GeminiModel | None = None,
    ) -> dict[str, Any]:
        """Generate structured JSON output from LLM."""
        return await self.llm.generate_json(
            prompt=prompt,
            system_instruction=self.system_prompt,
            response_schema=output_schema,
            model=model or self.default_model,
        )
