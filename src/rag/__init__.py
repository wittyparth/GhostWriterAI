"""
RAG Package - Retrieval Augmented Generation for LinkedIn content.

Exports:
    VectorStoreBase: Abstract vector store interface
    ChromaDBStore: ChromaDB implementation
    get_vector_store: Factory function
    RAGRetriever: High-level retrieval interface
    get_retriever: Retriever singleton
    EmbeddingService: Embedding generation with caching
    get_embedding_service: Embedding service singleton
"""

from src.rag.vectorstore import (
    VectorStoreBase,
    ChromaDBStore,
    get_vector_store,
)
from src.rag.retriever import (
    RAGRetriever,
    get_retriever,
)
from src.rag.embeddings import (
    EmbeddingService,
    get_embedding_service,
)

__all__ = [
    "VectorStoreBase",
    "ChromaDBStore",
    "get_vector_store",
    "RAGRetriever",
    "get_retriever",
    "EmbeddingService",
    "get_embedding_service",
]
