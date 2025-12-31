"""
RAG retriever for LinkedIn post knowledge base.

Provides high-level retrieval operations for finding relevant reference posts,
hooks, and structures from the vector store.
"""

import logging
from typing import Any

from src.config.constants import (
    RAG_TOP_K_DEFAULT,
    RAG_NAMESPACE_REFERENCE,
    RAG_NAMESPACE_HOOKS,
    RAG_NAMESPACE_STRUCTURES,
)
from src.rag.vectorstore import VectorStoreBase, get_vector_store

logger = logging.getLogger(__name__)


class RAGRetriever:
    """
    High-level retriever for LinkedIn content knowledge base.
    
    Provides methods for retrieving:
    - Reference posts for inspiration
    - Hook patterns and examples
    - Structure templates
    """
    
    def __init__(self, vector_store: VectorStoreBase | None = None):
        """
        Initialize the RAG retriever.
        
        Args:
            vector_store: Optional vector store instance (uses default if not provided)
        """
        self.store = vector_store or get_vector_store()
    
    async def get_similar_posts(
        self,
        idea: str,
        top_k: int = RAG_TOP_K_DEFAULT,
        format_filter: str | None = None,
        niche_filter: str | None = None,
        min_engagement: float | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve similar reference posts for inspiration.
        
        Args:
            idea: The content idea to find similar posts for
            top_k: Number of results to return
            format_filter: Filter by format (text, carousel, video)
            niche_filter: Filter by content niche
            min_engagement: Minimum engagement rate filter
            
        Returns:
            List of similar posts with content and metadata
        """
        # Build metadata filter
        filter_metadata = {}
        if format_filter:
            filter_metadata["format"] = format_filter
        if niche_filter:
            filter_metadata["niche"] = niche_filter
        if min_engagement:
            filter_metadata["engagement_rate"] = {"$gte": min_engagement}
        
        results = await self.store.search(
            query=idea,
            top_k=top_k,
            namespace=RAG_NAMESPACE_REFERENCE,
            filter_metadata=filter_metadata if filter_metadata else None,
        )
        
        # Sort by a combination of similarity and engagement
        for r in results:
            engagement = r.get("metadata", {}).get("engagement_rate", 0) or 0
            r["combined_score"] = r["score"] * 0.7 + (engagement / 10) * 0.3
        
        results.sort(key=lambda x: x.get("combined_score", 0), reverse=True)
        
        logger.info(f"Retrieved {len(results)} similar posts for idea")
        return results
    
    async def get_hook_examples(
        self,
        idea: str,
        hook_type: str | None = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Retrieve hook examples from the knowledge base.
        
        Args:
            idea: Content idea to match hooks for
            hook_type: Optional specific hook type to filter for
            top_k: Number of results to return
            
        Returns:
            List of hook examples with scores and metadata
        """
        filter_metadata = {}
        if hook_type:
            filter_metadata["hook_type"] = hook_type
        
        results = await self.store.search(
            query=idea,
            top_k=top_k,
            namespace=RAG_NAMESPACE_HOOKS,
            filter_metadata=filter_metadata if filter_metadata else None,
        )
        
        return results
    
    async def get_structure_templates(
        self,
        idea: str,
        structure_type: str | None = None,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Retrieve structure templates from the knowledge base.
        
        Args:
            idea: Content idea to match structures for
            structure_type: Optional specific structure type to filter
            top_k: Number of results to return
            
        Returns:
            List of structure templates with metadata
        """
        filter_metadata = {}
        if structure_type:
            filter_metadata["structure_type"] = structure_type
        
        results = await self.store.search(
            query=idea,
            top_k=top_k,
            namespace=RAG_NAMESPACE_STRUCTURES,
            filter_metadata=filter_metadata if filter_metadata else None,
        )
        
        return results
    
    async def add_reference_post(
        self,
        content: str,
        metadata: dict[str, Any],
        doc_id: str | None = None,
    ) -> str:
        """
        Add a reference post to the knowledge base.
        
        Args:
            content: Post content
            metadata: Post metadata (format, engagement, niche, etc.)
            doc_id: Optional custom document ID
            
        Returns:
            Document ID
        """
        ids = await self.store.add_documents(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id] if doc_id else None,
            namespace=RAG_NAMESPACE_REFERENCE,
        )
        return ids[0]
    
    async def add_hook_example(
        self,
        hook_text: str,
        metadata: dict[str, Any],
    ) -> str:
        """
        Add a hook example to the knowledge base.
        
        Args:
            hook_text: The hook text
            metadata: Hook metadata (type, score, source, etc.)
            
        Returns:
            Document ID
        """
        ids = await self.store.add_documents(
            documents=[hook_text],
            metadatas=[metadata],
            namespace=RAG_NAMESPACE_HOOKS,
        )
        return ids[0]
    
    async def add_structure_template(
        self,
        template: str,
        metadata: dict[str, Any],
    ) -> str:
        """
        Add a structure template to the knowledge base.
        
        Args:
            template: Structure template description
            metadata: Template metadata (type, use_cases, etc.)
            
        Returns:
            Document ID
        """
        ids = await self.store.add_documents(
            documents=[template],
            metadatas=[metadata],
            namespace=RAG_NAMESPACE_STRUCTURES,
        )
        return ids[0]
    
    async def build_context_for_agent(
        self,
        idea: str,
        agent_name: str,
        top_k: int = 5,
    ) -> dict[str, Any]:
        """
        Build a context package for an agent based on the idea.
        
        Args:
            idea: The content idea
            agent_name: Name of the agent requesting context
            top_k: Number of results per category
            
        Returns:
            Context dictionary with relevant references
        """
        context = {
            "similar_posts": [],
            "hook_examples": [],
            "structure_templates": [],
        }
        
        # Get similar posts for most agents
        if agent_name in ["validator", "strategist", "writer", "optimizer"]:
            context["similar_posts"] = await self.get_similar_posts(idea, top_k=top_k)
        
        # Get hooks for writer
        if agent_name in ["writer"]:
            context["hook_examples"] = await self.get_hook_examples(idea, top_k=top_k)
        
        # Get structures for strategist
        if agent_name in ["strategist"]:
            context["structure_templates"] = await self.get_structure_templates(idea, top_k=3)
        
        return context


# Singleton instance
_retriever: RAGRetriever | None = None


def get_retriever() -> RAGRetriever:
    """Get the RAG retriever singleton."""
    global _retriever
    if _retriever is None:
        _retriever = RAGRetriever()
    return _retriever
