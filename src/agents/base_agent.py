"""
Base Agent class for all LinkedIn content agents.

Provides common functionality for LLM interaction, error handling, retries, and logging.
"""

import logging
import time
import asyncio
from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic

from pydantic import BaseModel

from src.llm.gemini import GeminiClient, get_gemini_client
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
    - Token and cost tracking
    """
    
    agent_name: str = "base"
    max_retries: int = 3
    retry_delay: float = 1.0
    
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
        Execute the agent with timing, retries, and error handling.
        
        Returns dict with output and metadata.
        """
        start_time = time.time()
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = await self._execute(input_data)
                execution_time = int((time.time() - start_time) * 1000)
                
                logger.info(f"{self.agent_name} completed in {execution_time}ms (attempt {attempt + 1})")
                
                return {
                    "output": result.model_dump() if isinstance(result, BaseModel) else result,
                    "agent": self.agent_name,
                    "execution_time_ms": execution_time,
                    "status": "success",
                    "attempt": attempt + 1,
                }
            except Exception as e:
                last_error = e
                logger.warning(f"{self.agent_name} attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
        
        # All retries exhausted
        execution_time = int((time.time() - start_time) * 1000)
        logger.error(f"{self.agent_name} failed after {self.max_retries} attempts: {last_error}")
        
        return {
            "output": None,
            "agent": self.agent_name,
            "execution_time_ms": execution_time,
            "status": "error",
            "error": str(last_error),
            "attempts": self.max_retries,
        }
    
    async def generate_structured(
        self,
        prompt: str,
        output_schema: dict[str, Any] | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        """Generate structured JSON output from LLM."""
        return await self.llm.generate_json(
            prompt=prompt,
            system_instruction=self.system_prompt,
            response_schema=output_schema,
            model=model,
        )
    
    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        model: str | None = None,
    ) -> str:
        """Generate free-form text output from LLM."""
        return await self.llm.generate(
            prompt=prompt,
            system_instruction=self.system_prompt,
            temperature=temperature,
            model=model,
        )
    
    def get_token_usage(self) -> dict[str, int]:
        """Get token usage statistics from LLM client."""
        return {
            "input_tokens": self.llm.total_input_tokens,
            "output_tokens": self.llm.total_output_tokens,
        }
    
    def get_cost_estimate(self) -> dict[str, float]:
        """Get cost estimate from LLM client."""
        return self.llm.get_cost_estimate()
