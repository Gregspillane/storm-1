import os
import unittest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from knowledge_storm.storm_wiki.modules.retriever import RAGRetriever, PrimaryRAGRetriever
from knowledge_storm.interface import Retriever, Information

class TestRAGRetriever(unittest.TestCase):
    def setUp(self):
        load_dotenv()
        self.retriever = RAGRetriever()
        
    def test_single_query_retrieve(self):
        """Test retrieving with a single query string"""
        query = "What is RAG?"
        results = self.retriever.retrieve(query)
        self.assertIsInstance(results, list)
        if results:  # If API returns results
            self.assertIsInstance(results[0], Information)
            self.assertIn("score", results[0].meta)
            
    def test_multiple_query_retrieve(self):
        """Test retrieving with multiple queries"""
        queries = ["What is RAG?", "How does RAG work?"]
        results = self.retriever.retrieve(queries)
        self.assertIsInstance(results, list)
        if results:  # If API returns results
            self.assertIsInstance(results[0], Information)
            self.assertIn("score", results[0].meta)
            
    def test_exclude_urls(self):
        """Test URL exclusion functionality"""
        query = "What is RAG?"
        exclude_urls = ["https://example.com"]
        results = self.retriever.retrieve(query, exclude_urls=exclude_urls)
        if results:  # If API returns results
            for result in results:
                self.assertNotIn(result.url, exclude_urls)
                
    def test_rate_limit_handling(self):
        """Test rate limit handling with exponential backoff"""
        with patch('requests.Session.post') as mock_post:
            # Simulate rate limit response first, then success
            mock_post.side_effect = [
                MagicMock(status_code=429, headers={'Retry-After': '1'}),
                MagicMock(status_code=200, json=lambda: {'matches': []})
            ]
            results = self.retriever.retrieve("test query")
            self.assertEqual(mock_post.call_count, 2)

class TestPrimaryRAGRetriever(unittest.TestCase):
    def setUp(self):
        load_dotenv()
        self.rag_retriever = RAGRetriever()
        self.web_retriever = MagicMock(spec=Retriever)
        self.primary_retriever = PrimaryRAGRetriever(self.rag_retriever, self.web_retriever)
        
    def test_rag_priority(self):
        """Test that RAG results above threshold are prioritized"""
        # Mock RAG results with high score
        mock_result = Information(
            url="1",
            description="",
            snippets=["test"],
            title="",
            meta={"score": 0.9}
        )
        with patch.object(self.rag_retriever, 'retrieve', return_value=[mock_result]):
            results = self.primary_retriever.retrieve("test query")
            self.assertEqual(results[0].meta["score"], 0.9)
            self.web_retriever.retrieve.assert_not_called()
            
    def test_web_fallback(self):
        """Test fallback to web search when RAG results are below threshold"""
        # Mock RAG results with low score
        mock_rag_result = Information(
            url="1",
            description="",
            snippets=["test"],
            title="",
            meta={"score": 0.5}
        )
        mock_web_result = Information(
            url="2",
            description="",
            snippets=["test"],
            title="",
            meta={"score": 0.8}
        )
        
        with patch.object(self.rag_retriever, 'retrieve', return_value=[mock_rag_result]):
            self.web_retriever.retrieve.return_value = [mock_web_result]
            results = self.primary_retriever.retrieve("test query")
            self.assertEqual(results[0].meta["score"], 0.8)
            self.web_retriever.retrieve.assert_called_once()
            
    def test_web_fallback_on_error(self):
        """Test fallback to web search when RAG retrieval fails"""
        mock_web_result = Information(
            url="2",
            description="",
            snippets=["test"],
            title="",
            meta={"score": 0.8}
        )
        
        with patch.object(self.rag_retriever, 'retrieve', side_effect=Exception("API Error")):
            self.web_retriever.retrieve.return_value = [mock_web_result]
            results = self.primary_retriever.retrieve("test query")
            self.assertEqual(results[0].meta["score"], 0.8)
            self.web_retriever.retrieve.assert_called_once()
            
    def test_exclude_urls_propagation(self):
        """Test that exclude_urls is properly propagated to both retrievers"""
        exclude_urls = ["https://example.com"]
        query = "test query"
        
        self.primary_retriever.retrieve(query, exclude_urls=exclude_urls)
        
        # Verify exclude_urls was passed to both retrievers
        self.web_retriever.retrieve.assert_called_with(query, exclude_urls=exclude_urls)

if __name__ == '__main__':
    unittest.main()