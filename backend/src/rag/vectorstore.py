"""
Vector store abstraction layer.

Provides a unified interface for ChromaDB (local dev) and Pinecone (production).
Uses Gemini embeddings for vector generation.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any
from uuid import uuid4

from src.config.settings import get_settings
from src.config.constants import (
    RAG_TOP_K_DEFAULT,
    RAG_SIMILARITY_THRESHOLD,
    EMBEDDING_DIMENSION,
)
from src.llm.gemini import get_gemini_client

logger = logging.getLogger(__name__)


class VectorStoreBase(ABC):
    """Abstract base class for vector store implementations."""
    
    @abstractmethod
    async def add_documents(
        self,
        documents: list[str],
        metadatas: list[dict[str, Any]] | None = None,
        ids: list[str] | None = None,
        namespace: str | None = None,
    ) -> list[str]:
        """Add documents to the vector store."""
        pass
    
    @abstractmethod
    async def search(
        self,
        query: str,
        top_k: int = RAG_TOP_K_DEFAULT,
        namespace: str | None = None,
        filter_metadata: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search for similar documents."""
        pass
    
    @abstractmethod
    async def delete(
        self,
        ids: list[str],
        namespace: str | None = None,
    ) -> None:
        """Delete documents by ID."""
        pass
    
    @abstractmethod
    async def get_by_id(
        self,
        doc_id: str,
        namespace: str | None = None,
    ) -> dict[str, Any] | None:
        """Get a document by its ID."""
        pass


class ChromaDBStore(VectorStoreBase):
    """
    ChromaDB implementation for local development.
    
    Uses persistent storage for development/testing.
    """
    
    def __init__(self, collection_name: str = "linkedin_posts"):
        """
        Initialize ChromaDB vector store.
        
        Args:
            collection_name: Name of the ChromaDB collection
        """
        self.settings = get_settings()
        self.collection_name = collection_name
        self._client = None
        self._collection = None
        self._gemini = get_gemini_client()
    
    @property
    def client(self):
        """Lazy-load ChromaDB client."""
        if self._client is None:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            
            self._client = chromadb.Client(ChromaSettings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=self.settings.chromadb_path,
                anonymized_telemetry=False,
            ))
            logger.info(f"ChromaDB client initialized: {self.settings.chromadb_path}")
        return self._client
    
    def _get_collection(self, namespace: str | None = None):
        """Get or create a collection."""
        name = f"{self.collection_name}_{namespace}" if namespace else self.collection_name
        return self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )
    
    async def add_documents(
        self,
        documents: list[str],
        metadatas: list[dict[str, Any]] | None = None,
        ids: list[str] | None = None,
        namespace: str | None = None,
    ) -> list[str]:
        """
        Add documents to ChromaDB.
        
        Args:
            documents: List of document texts
            metadatas: Optional metadata for each document
            ids: Optional custom IDs (generated if not provided)
            namespace: Optional namespace for organization
            
        Returns:
            List of document IDs
        """
        if not documents:
            return []
        
        # Generate IDs if not provided
        doc_ids = ids or [str(uuid4()) for _ in documents]
        
        # Generate embeddings
        embeddings = await self._gemini.embed(documents, task_type="retrieval_document")
        
        # Prepare metadata
        metas = metadatas or [{} for _ in documents]
        
        # Add to collection
        collection = self._get_collection(namespace)
        collection.add(
            ids=doc_ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metas,
        )
        
        logger.info(f"Added {len(documents)} documents to ChromaDB (namespace: {namespace})")
        return doc_ids
    
    async def search(
        self,
        query: str,
        top_k: int = RAG_TOP_K_DEFAULT,
        namespace: str | None = None,
        filter_metadata: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            namespace: Optional namespace to search within
            filter_metadata: Optional metadata filter
            
        Returns:
            List of matching documents with scores
        """
        # Generate query embedding
        query_embedding = await self._gemini.embed_single(query, task_type="retrieval_query")
        
        collection = self._get_collection(namespace)
        
        # Build query params
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
            "include": ["documents", "metadatas", "distances"],
        }
        
        if filter_metadata:
            query_params["where"] = filter_metadata
        
        results = collection.query(**query_params)
        
        # Format results
        formatted = []
        for i in range(len(results["ids"][0])):
            # Convert distance to similarity score (cosine distance -> similarity)
            distance = results["distances"][0][i] if results["distances"] else 0
            similarity = 1 - distance  # Cosine similarity
            
            if similarity >= RAG_SIMILARITY_THRESHOLD:
                formatted.append({
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i] if results["documents"] else "",
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "score": similarity,
                })
        
        logger.debug(f"Search returned {len(formatted)} results for query: {query[:50]}...")
        return formatted
    
    async def delete(
        self,
        ids: list[str],
        namespace: str | None = None,
    ) -> None:
        """Delete documents by ID."""
        collection = self._get_collection(namespace)
        collection.delete(ids=ids)
        logger.info(f"Deleted {len(ids)} documents from ChromaDB")
    
    async def get_by_id(
        self,
        doc_id: str,
        namespace: str | None = None,
    ) -> dict[str, Any] | None:
        """Get a document by its ID."""
        collection = self._get_collection(namespace)
        result = collection.get(ids=[doc_id], include=["documents", "metadatas"])
        
        if not result["ids"]:
            return None
        
        return {
            "id": result["ids"][0],
            "content": result["documents"][0] if result["documents"] else "",
            "metadata": result["metadatas"][0] if result["metadatas"] else {},
        }
    
    def persist(self):
        """Persist ChromaDB to disk."""
        if self._client:
            self._client.persist()
            logger.info("ChromaDB persisted to disk")


class PineconeStore(VectorStoreBase):
    """
    Pinecone implementation for production.
    """
    
    def __init__(self, index_name: str | None = None):
        """
        Initialize Pinecone vector store.
        """
        self.settings = get_settings()
        self.index_name = index_name or self.settings.pinecone_index_name
        self._index = None
        self._gemini = get_gemini_client()
        
    @property
    def index(self):
        """Lazy-load Pinecone index."""
        if self._index is None:
            from pinecone import Pinecone
            
            if not self.settings.pinecone_api_key:
                raise ValueError("Pinecone API key not found in settings")
                
            pc = Pinecone(api_key=self.settings.pinecone_api_key.get_secret_value())
            self._index = pc.Index(self.index_name)
            logger.info(f"Pinecone index initialized: {self.index_name}")
            
        return self._index
    
    async def add_documents(
        self,
        documents: list[str],
        metadatas: list[dict[str, Any]] | None = None,
        ids: list[str] | None = None,
        namespace: str | None = None,
    ) -> list[str]:
        """Add documents to Pinecone."""
        if not documents:
            return []
            
        # Generate IDs if not provided
        doc_ids = ids or [str(uuid4()) for _ in documents]
        
        # Generate embeddings
        embeddings = await self._gemini.embed(documents, task_type="retrieval_document")
        
        # Prepare batch for upsert
        vectors = []
        metas = metadatas or [{} for _ in documents]
        
        for i, (doc, meta, emb, doc_id) in enumerate(zip(documents, metas, embeddings, doc_ids)):
            # Pinecone metadata must be int, float, str, bool, or list of strings
            # We add the content as "text" in metadata for retrieval
            safe_meta = meta.copy()
            safe_meta["text"] = doc
            
            vectors.append({
                "id": doc_id,
                "values": emb,
                "metadata": safe_meta
            })
            
        # Upsert to Pinecone
        self.index.upsert(vectors=vectors, namespace=namespace or "")
        
        logger.info(f"Added {len(documents)} documents to Pinecone (namespace: {namespace})")
        return doc_ids
    
    async def search(
        self,
        query: str,
        top_k: int = RAG_TOP_K_DEFAULT,
        namespace: str | None = None,
        filter_metadata: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search Pinecone."""
        # Generate query embedding
        query_embedding = await self._gemini.embed_single(query, task_type="retrieval_query")
        
        response = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            namespace=namespace or "",
            include_metadata=True,
            filter=filter_metadata
        )
        
        formatted = []
        for match in response.matches:
            if match.score >= RAG_SIMILARITY_THRESHOLD:
                meta = match.metadata or {}
                content = meta.pop("text", "") # Extract content from metadata
                
                formatted.append({
                    "id": match.id,
                    "content": content,
                    "metadata": meta,
                    "score": match.score,
                })
                
        return formatted
    
    async def delete(
        self,
        ids: list[str],
        namespace: str | None = None,
    ) -> None:
        """Delete from Pinecone."""
        self.index.delete(ids=ids, namespace=namespace or "")
        logger.info(f"Deleted {len(ids)} documents from Pinecone")
        
    async def get_by_id(
        self,
        doc_id: str,
        namespace: str | None = None,
    ) -> dict[str, Any] | None:
        """Get doc by ID."""
        response = self.index.fetch(ids=[doc_id], namespace=namespace or "")
        
        if not response.vectors or doc_id not in response.vectors:
            return None
            
        vector = response.vectors[doc_id]
        meta = vector.metadata or {}
        content = meta.pop("text", "")
        
        return {
            "id": vector.id,
            "content": content,
            "metadata": meta,
        }


# Factory function
def get_vector_store(store_type: str | None = None) -> VectorStoreBase:
    """
    Get a vector store instance.
    
    Args:
        store_type: Type of store ("chromadb" or "pinecone"). 
                   If None, auto-detects based on settings/env.
        
    Returns:
        Vector store instance
    """
    settings = get_settings()
    
    # Auto-detect if not specified
    if store_type is None:
        if settings.pinecone_api_key and settings.pinecone_api_key.get_secret_value():
            store_type = "pinecone"
        else:
            store_type = "chromadb"
            
    if store_type == "chromadb":
        return ChromaDBStore()
    elif store_type == "pinecone":
        return PineconeStore()
    else:
        raise ValueError(f"Unknown vector store type: {store_type}")
