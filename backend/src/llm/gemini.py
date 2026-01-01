"""
Google Gemini API client wrapper.

Provides async interface for text generation and embeddings.
Uses the model specified in .env (GEMINI_MODEL), falls back to gemini-2.5-flash.
"""

import json
import logging
from typing import Any

from google import genai
from google.genai import types

from src.config.settings import get_settings
from src.config.constants import (
    COST_INPUT_PER_MILLION,
    COST_OUTPUT_PER_MILLION,
    COST_EMBEDDING_PER_MILLION,
)

logger = logging.getLogger(__name__)

# Default fallback model
DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_EMBEDDING_MODEL = "text-embedding-004"


class GeminiClient:
    """
    Simple client for Google Gemini API.
    
    Uses model from settings (GEMINI_MODEL env var).
    Falls back to gemini-2.5-flash if not specified.
    """

    def __init__(self, model: str | None = None):
        """
        Initialize the Gemini client.
        
        Args:
            model: Override model name (optional)
        """
        self.settings = get_settings()
        
        # Initialize client with API key
        self.client = genai.Client(api_key=self.settings.gemini_api_key.get_secret_value())
        
        # Use provided model, or from settings, or default
        self.model = model or self.settings.gemini_model or DEFAULT_MODEL
        self.embedding_model = self.settings.embedding_model or DEFAULT_EMBEDDING_MODEL
        
        # Token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_embedding_tokens = 0
        
        logger.info(f"GeminiClient initialized with model: {self.model}")

    async def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.7,
        max_output_tokens: int = 4096,
        response_schema: dict[str, Any] | None = None,
        model: str | None = None,
    ) -> str:
        """
        Generate text response from Gemini.
        
        Args:
            prompt: The user prompt
            system_instruction: System instruction for context
            temperature: Sampling temperature (0-2)
            max_output_tokens: Maximum output tokens
            response_schema: JSON schema for structured output
            model: Override model for this call
            
        Returns:
            Generated text
        """
        try:
            model_name = model or self.model

            # Build config
            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
            
            if system_instruction:
                config.system_instruction = system_instruction
            
            if response_schema:
                config.response_mime_type = "application/json"
                config.response_schema = response_schema

            # Generate
            response = await self.client.aio.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config,
            )

            # Track tokens
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                self.total_input_tokens += response.usage_metadata.prompt_token_count or 0
                self.total_output_tokens += response.usage_metadata.candidates_token_count or 0

            return response.text

        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise

    async def generate_json(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.3,
        max_output_tokens: int = 4096,
        response_schema: dict[str, Any] | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        """Generate a JSON response."""
        json_prompt = prompt
        if not response_schema:
            json_prompt = f"{prompt}\n\nRespond ONLY with valid JSON, no other text."
        
        response_text = await self.generate(
            prompt=json_prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            response_schema=response_schema,
            model=model,
        )
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise ValueError(f"Invalid JSON from Gemini: {e}")

    async def embed(self, texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
        """Generate embeddings for texts."""
        try:
            embeddings = []
            
            for i in range(0, len(texts), 100):
                batch = texts[i:i + 100]
                
                result = await self.client.aio.models.embed_content(
                    model=self.embedding_model,
                    contents=batch,
                    config=types.EmbedContentConfig(task_type=task_type),
                )
                
                for emb in result.embeddings:
                    embeddings.append(emb.values)
                
                self.total_embedding_tokens += sum(len(t) // 4 for t in batch)

            return embeddings

        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            raise

    async def embed_single(self, text: str, task_type: str = "RETRIEVAL_QUERY") -> list[float]:
        """Generate embedding for a single text."""
        embeddings = await self.embed([text], task_type=task_type)
        return embeddings[0]

    def get_cost_estimate(self) -> dict[str, float]:
        """Get cost estimate based on token usage."""
        input_cost = (self.total_input_tokens / 1_000_000) * COST_INPUT_PER_MILLION
        output_cost = (self.total_output_tokens / 1_000_000) * COST_OUTPUT_PER_MILLION
        embedding_cost = (self.total_embedding_tokens / 1_000_000) * COST_EMBEDDING_PER_MILLION
        
        return {
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "embedding_tokens": self.total_embedding_tokens,
            "total_cost_usd": round(input_cost + output_cost + embedding_cost, 6),
        }

    def reset_token_counts(self):
        """Reset token counters."""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_embedding_tokens = 0


# Singleton
_gemini_client: GeminiClient | None = None


def get_gemini_client() -> GeminiClient:
    """Get the Gemini client singleton."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
