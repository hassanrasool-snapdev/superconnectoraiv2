import unittest
from unittest.mock import patch, MagicMock
from app.services.retrieval_service import RetrievalService
from app.services.threading_service import threading_service

class TestThreadingService(unittest.TestCase):

    def setUp(self):
        self.retrieval_service = RetrievalService()

    @patch('app.services.retrieval_service.RetrievalService._rerank_chunk')
    def test_rerank_with_gemini_parallel(self, mock_rerank_chunk):
        # Mock the behavior of _rerank_chunk
        def side_effect(chunk, user_query):
            # Simulate processing and return a result for each item in the chunk
            return [{'profile': item, 'score': 0.9} for item in chunk]
        
        mock_rerank_chunk.side_effect = side_effect

        # Sample data
        candidates = [{'id': i} for i in range(25)]
        user_query = "test query"

        # Call the method that uses the threading service
        results = self.retrieval_service.rerank_with_gemini(candidates, user_query)

        # Assertions
        self.assertEqual(len(results), 25)
        self.assertEqual(mock_rerank_chunk.call_count, 3)  # 25 candidates, chunk size 10 -> 3 chunks

if __name__ == '__main__':
    unittest.main()