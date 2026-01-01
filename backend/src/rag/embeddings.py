"""
Embedding service using Gemini embeddings.

Provides batch processing, caching, and embedding generation.
"""

import logging
from typing import Any
import hashlib

from src.llm.gemini import get_gemini_client
from src.config.constants import EMBEDDING_DIMENSION

logger = logging.getLogger(__name__)

# Default embedding model
DEFAULT_EMBEDDING_MODEL = "text-embedding-004"


class EmbeddingService:
    """
    Service for generating embeddings using Gemini.
    
    Features:
    - Batch processing for efficiency
    - Simple in-memory caching
    - Configurable embedding model
    """
    
    def __init__(self, model: str = DEFAULT_EMBEDDING_MODEL):
        self.client = get_gemini_client()
        self.model = model
        self._cache: dict[str, list[float]] = {}
    
    def _cache_key(self, text: str, task_type: str) -> str:
        """Generate cache key for embedding."""
        content = f"{text}:{task_type}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def embed_text(
        self,
        text: str,
        task_type: str = "retrieval_document",
        use_cache: bool = True,
    ) -> list[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            task_type: retrieval_document, retrieval_query, or semantic_similarity
            use_cache: Whether to use cached embeddings
            
        Returns:
            Embedding vector (768 dimensions for text-embedding-004)
        """
        cache_key = self._cache_key(text, task_type)
        
        if use_cache and cache_key in self._cache:
            logger.debug(f"Embedding cache hit for: {text[:50]}...")
            return self._cache[cache_key]
        
        embedding = await self.client.embed_single(text, task_type=task_type)
        
        if use_cache:
            self._cache[cache_key] = embedding
        
        return embedding
    
    async def embed_texts(
        self,
        texts: list[str],
        task_type: str = "retrieval_document",
        use_cache: bool = True,
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            task_type: Type of embedding task
            use_cache: Whether to use cached embeddings
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        results = []
        texts_to_embed = []
        indices_to_embed = []
        
        # Check cache first
        for i, text in enumerate(texts):
            cache_key = self._cache_key(text, task_type)
            if use_cache and cache_key in self._cache:
                results.append((i, self._cache[cache_key]))
            else:
                texts_to_embed.append(text)
                indices_to_embed.append(i)
        
        # Embed uncached texts
        if texts_to_embed:
            new_embeddings = await self.client.embed(texts_to_embed, task_type=task_type)
            
            for idx, embedding in zip(indices_to_embed, new_embeddings):
                results.append((idx, embedding))
                if use_cache:
                    cache_key = self._cache_key(texts[idx], task_type)
                    self._cache[cache_key] = embedding
        
        # Sort by original index and return embeddings only
        results.sort(key=lambda x: x[0])
        return [emb for _, emb in results]
    
    async def embed_for_query(self, query: str) -> list[float]:
        """Embed text optimized for query matching."""
        return await self.embed_text(query, task_type="retrieval_query")
    
    async def embed_for_indexing(self, document: str) -> list[float]:
        """Embed text optimized for document indexing."""
        return await self.embed_text(document, task_type="retrieval_document")
    
    async def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts.
        
        Returns:
            Similarity score between 0 and 1
        """
        emb1 = await self.embed_text(text1, task_type="semantic_similarity")
        emb2 = await self.embed_text(text2, task_type="semantic_similarity")
        
        # Cosine similarity
        dot_product = sum(a * b for a, b in zip(emb1, emb2))
        norm1 = sum(a * a for a in emb1) ** 0.5
        norm2 = sum(b * b for b in emb2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def clear_cache(self):
        """Clear the embedding cache."""
        self._cache.clear()
        logger.info("Embedding cache cleared")
    
    @property
    def cache_size(self) -> int:
        """Get number of cached embeddings."""
        return len(self._cache)


# Singleton
_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """Get the embedding service singleton."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
