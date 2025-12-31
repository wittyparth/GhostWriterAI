"""
Unit tests for RAG system.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestEmbeddingService:
    """Tests for embedding service."""
    
    @pytest.fixture
    def mock_gemini_client(self):
        """Create mock Gemini client."""
        client = MagicMock()
        client.embed = AsyncMock(return_value=[[0.1] * 768])
        client.embed_single = AsyncMock(return_value=[0.1] * 768)
        return client
    
    @pytest.mark.asyncio
    async def test_embed_text_returns_vector(self, mock_gemini_client):
        """Test that embed_text returns a vector."""
        from src.rag.embeddings import EmbeddingService
        
        with patch('src.rag.embeddings.get_gemini_client', return_value=mock_gemini_client):
            service = EmbeddingService()
            service.client = mock_gemini_client
            
            result = await service.embed_text("Test text")
            
            assert isinstance(result, list)
            assert len(result) == 768
    
    @pytest.mark.asyncio
    async def test_embed_caching(self, mock_gemini_client):
        """Test that embeddings are cached."""
        from src.rag.embeddings import EmbeddingService
        
        with patch('src.rag.embeddings.get_gemini_client', return_value=mock_gemini_client):
            service = EmbeddingService()
            service.client = mock_gemini_client
            
            # First call
            await service.embed_text("Test text", use_cache=True)
            
            # Second call should use cache
            await service.embed_text("Test text", use_cache=True)
            
            # Should only call API once due to caching
            assert service.cache_size >= 1


class TestRAGRetriever:
    """Tests for RAG retriever."""
    
    @pytest.fixture
    def mock_vector_store(self):
        """Create mock vector store."""
        store = MagicMock()
        store.search = AsyncMock(return_value=[
            {"id": "1", "content": "Test post", "score": 0.9, "metadata": {}},
        ])
        store.add_documents = AsyncMock(return_value=["doc1"])
        return store
    
    @pytest.mark.asyncio
    async def test_get_similar_posts(self, mock_vector_store):
        """Test retrieving similar posts."""
        from src.rag.retriever import RAGRetriever
        
        retriever = RAGRetriever(vector_store=mock_vector_store)
        
        results = await retriever.get_similar_posts("startup lessons", top_k=5)
        
        assert isinstance(results, list)
        mock_vector_store.search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_reference_post(self, mock_vector_store):
        """Test adding a reference post."""
        from src.rag.retriever import RAGRetriever
        
        retriever = RAGRetriever(vector_store=mock_vector_store)
        
        doc_id = await retriever.add_reference_post(
            content="Test post content",
            metadata={"format": "text", "engagement_rate": 0.05},
        )
        
        assert doc_id == "doc1"
        mock_vector_store.add_documents.assert_called_once()
