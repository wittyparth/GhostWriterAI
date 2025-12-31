"""
Google Gemini API client wrapper.

Provides async interface for text generation and embeddings using Gemini models.
Supports swappable models: Gemini 3 Flash, Gemini 3 Pro, Gemini 2.5 Flash, etc.
"""

import json
import logging
from enum import Enum
from typing import Any

import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from src.config.settings import get_settings
from src.config.constants import (
    COST_INPUT_PER_MILLION,
    COST_OUTPUT_PER_MILLION,
    COST_EMBEDDING_PER_MILLION,
)

logger = logging.getLogger(__name__)


class GeminiModel(str, Enum):
    """Available Gemini models for generation."""
    
    # Gemini 3 models (latest)
    GEMINI_3_FLASH = "gemini-3-flash-preview"
    GEMINI_3_PRO = "gemini-3-pro-preview"
    
    # Gemini 2.5 models
    GEMINI_25_FLASH = "gemini-2.5-flash"
    GEMINI_25_FLASH_LITE = "gemini-2.5-flash-lite"
    GEMINI_25_PRO = "gemini-2.5-pro"
    
    # Gemini 2.0 models (stable)
    GEMINI_20_FLASH = "gemini-2.0-flash"
    GEMINI_20_FLASH_LITE = "gemini-2.0-flash-lite"


class EmbeddingModel(str, Enum):
    """Available embedding models."""
    
    TEXT_EMBEDDING_004 = "text-embedding-004"  # Latest, 768 dimensions
    TEXT_EMBEDDING_005 = "text-embedding-005"  # If available


# Model cost mapping (USD per 1M tokens) - approximate
MODEL_COSTS = {
    GeminiModel.GEMINI_3_FLASH: {"input": 0.075, "output": 0.30},
    GeminiModel.GEMINI_3_PRO: {"input": 0.50, "output": 2.00},
    GeminiModel.GEMINI_25_FLASH: {"input": 0.075, "output": 0.30},
    GeminiModel.GEMINI_25_PRO: {"input": 1.25, "output": 5.00},
    GeminiModel.GEMINI_20_FLASH: {"input": 0.075, "output": 0.30},
}


class GeminiClient:
    """
    Client for Google Gemini API with structured output support.
    
    Supports multiple Gemini models with easy swapping.
    Default: Gemini 3 Flash Preview (fastest and most capable).
    
    Usage:
        client = GeminiClient()
        
        # Use default model (Flash)
        response = await client.generate("Hello")
        
        # Use Pro for complex reasoning
        response = await client.generate("Complex task", model=GeminiModel.GEMINI_3_PRO)
        
        # Switch default model
        client.set_default_model(GeminiModel.GEMINI_3_PRO)
    """

    def __init__(
        self,
        default_model: GeminiModel | str | None = None,
        embedding_model: EmbeddingModel | str | None = None,
    ):
        """
        Initialize the Gemini client with API key from settings.
        
        Args:
            default_model: Default model to use (overrides settings)
            embedding_model: Embedding model to use (overrides settings)
        """
        self.settings = get_settings()
        genai.configure(api_key=self.settings.gemini_api_key.get_secret_value())
        
        # Set default models
        if default_model:
            self.default_model = GeminiModel(default_model) if isinstance(default_model, str) else default_model
        else:
            self.default_model = GeminiModel(self.settings.gemini_model)
            
        if embedding_model:
            self.embedding_model = EmbeddingModel(embedding_model) if isinstance(embedding_model, str) else embedding_model
        else:
            self.embedding_model = EmbeddingModel(self.settings.embedding_model)
        
        # Cache for initialized models
        self._model_cache: dict[str, genai.GenerativeModel] = {}
        
        # Track token usage for cost monitoring
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_embedding_tokens = 0
        
        logger.info(f"GeminiClient initialized with model: {self.default_model.value}")

    def set_default_model(self, model: GeminiModel | str) -> None:
        """
        Change the default model.
        
        Args:
            model: New default model
        """
        self.default_model = GeminiModel(model) if isinstance(model, str) else model
        logger.info(f"Default model changed to: {self.default_model.value}")

    def _get_model(
        self,
        model: GeminiModel | str | None = None,
        system_instruction: str | None = None,
    ) -> genai.GenerativeModel:
        """
        Get or create a GenerativeModel instance.
        
        Args:
            model: Model to use (defaults to self.default_model)
            system_instruction: Optional system instruction
            
        Returns:
            GenerativeModel instance
        """
        model_enum = GeminiModel(model) if isinstance(model, str) else (model or self.default_model)
        model_name = model_enum.value
        
        # Create cache key including system instruction
        cache_key = f"{model_name}:{hash(system_instruction or '')}"
        
        if cache_key not in self._model_cache:
            self._model_cache[cache_key] = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_instruction,
            )
        
        return self._model_cache[cache_key]

    async def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.7,
        max_output_tokens: int = 4096,
        response_schema: dict[str, Any] | None = None,
        model: GeminiModel | str | None = None,
    ) -> str:
        """
        Generate text response from Gemini.
        
        Args:
            prompt: The user prompt
            system_instruction: Optional system instruction for context
            temperature: Sampling temperature (0-2)
            max_output_tokens: Maximum tokens in response
            response_schema: Optional JSON schema for structured output
            model: Specific model to use (overrides default)
            
        Returns:
            Generated text response
        """
        try:
            # Get model (uses default if not specified)
            gen_model = self._get_model(model=model, system_instruction=system_instruction)

            # Configure generation
            generation_config = GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
            
            # Add response schema for structured output
            if response_schema:
                generation_config = GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    response_mime_type="application/json",
                    response_schema=response_schema,
                )

            # Generate response
            response = await gen_model.generate_content_async(
                prompt,
                generation_config=generation_config,
            )

            # Track token usage
            if hasattr(response, 'usage_metadata'):
                self.total_input_tokens += response.usage_metadata.prompt_token_count
                self.total_output_tokens += response.usage_metadata.candidates_token_count
                logger.debug(
                    f"Tokens used - Input: {response.usage_metadata.prompt_token_count}, "
                    f"Output: {response.usage_metadata.candidates_token_count}"
                )

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
        model: GeminiModel | str | None = None,
    ) -> dict[str, Any]:
        """
        Generate a JSON response from Gemini.
        
        Args:
            prompt: The user prompt
            system_instruction: Optional system instruction
            temperature: Lower temperature for more deterministic JSON
            max_output_tokens: Maximum tokens in response
            response_schema: Optional JSON schema for validation
            
        Returns:
            Parsed JSON dictionary
        """
        # Enhance prompt for JSON output
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
            # Parse JSON response
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {response_text[:500]}")
            raise ValueError(f"Invalid JSON response from Gemini: {e}")

    async def embed(
        self,
        texts: list[str],
        task_type: str = "retrieval_document",
    ) -> list[list[float]]:
        """
        Generate embeddings for texts.
        
        Args:
            texts: List of texts to embed
            task_type: Type of embedding task
                - "retrieval_document": For indexing documents
                - "retrieval_query": For search queries
                - "semantic_similarity": For comparing texts
                
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = []
            
            # Process in batches to avoid rate limits
            batch_size = 100
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                result = genai.embed_content(
                    model=f"models/{self.settings.embedding_model}",
                    content=batch,
                    task_type=task_type,
                )
                
                # Handle single vs multiple embeddings
                if len(batch) == 1:
                    embeddings.append(result['embedding'])
                else:
                    embeddings.extend(result['embedding'])
                
                # Track tokens (approximate - 1 token ≈ 4 chars)
                token_count = sum(len(t) // 4 for t in batch)
                self.total_embedding_tokens += token_count

            return embeddings

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise

    async def embed_single(
        self,
        text: str,
        task_type: str = "retrieval_query",
    ) -> list[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            task_type: Type of embedding task
            
        Returns:
            Embedding vector
        """
        embeddings = await self.embed([text], task_type=task_type)
        return embeddings[0]

    def get_cost_estimate(self) -> dict[str, float]:
        """
        Calculate estimated cost based on token usage.
        
        Returns:
            Dictionary with cost breakdown
        """
        input_cost = (self.total_input_tokens / 1_000_000) * COST_INPUT_PER_MILLION
        output_cost = (self.total_output_tokens / 1_000_000) * COST_OUTPUT_PER_MILLION
        embedding_cost = (self.total_embedding_tokens / 1_000_000) * COST_EMBEDDING_PER_MILLION
        
        return {
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "embedding_tokens": self.total_embedding_tokens,
            "input_cost_usd": round(input_cost, 6),
            "output_cost_usd": round(output_cost, 6),
            "embedding_cost_usd": round(embedding_cost, 6),
            "total_cost_usd": round(input_cost + output_cost + embedding_cost, 6),
        }

    def reset_token_counts(self):
        """Reset token counters."""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_embedding_tokens = 0


# Singleton instance
_gemini_client: GeminiClient | None = None


def get_gemini_client() -> GeminiClient:
    """
    Get or create the Gemini client singleton.
    
    Returns:
        GeminiClient instance
    """
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
