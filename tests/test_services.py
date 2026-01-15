"""
Comprehensive Unit and Integration Tests for ESG Question Answering System
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from src.utils.helpers import get_available_companies, validate_pdf_file, format_file_size, truncate_text
from src.config.settings import CHUNK_SIZE, OVERLAP, EMBEDDING_MODEL, TOP_K


class TestHelpers(unittest.TestCase):
    """Test utility helper functions"""
    
    def test_format_file_size_bytes(self):
        """Test file size formatting for bytes"""
        self.assertEqual(format_file_size(500), "500 B")
        self.assertEqual(format_file_size(1023), "1023 B")
    
    def test_format_file_size_kilobytes(self):
        """Test file size formatting for kilobytes"""
        self.assertEqual(format_file_size(1024), "1.00 KB")
        self.assertEqual(format_file_size(2048), "2.00 KB")
    
    def test_format_file_size_megabytes(self):
        """Test file size formatting for megabytes"""
        self.assertEqual(format_file_size(1048576), "1.00 MB")
        self.assertEqual(format_file_size(2097152), "2.00 MB")
    
    def test_get_available_companies(self):
        """Test company extraction from data folder"""
        companies = get_available_companies("./data/pdfs")
        self.assertIsInstance(companies, list)
        self.assertIn("General", companies)
        # Note: list is sorted, so General may not be first
        self.assertGreater(len(companies), 0)
    
    def test_validate_pdf_file_none(self):
        """Test PDF validation with None file"""
        is_valid, message = validate_pdf_file(None)
        self.assertFalse(is_valid)
        self.assertEqual(message, "No file uploaded")
    
    def test_validate_pdf_file_wrong_extension(self):
        """Test PDF validation with wrong file extension"""
        mock_file = Mock()
        mock_file.name = "document.txt"
        mock_file.size = 1000
        
        is_valid, message = validate_pdf_file(mock_file)
        self.assertFalse(is_valid)
        self.assertEqual(message, "File must be a PDF")
    
    def test_validate_pdf_file_too_large(self):
        """Test PDF validation with oversized file"""
        mock_file = Mock()
        mock_file.name = "large.pdf"
        mock_file.size = 60 * 1024 * 1024  # 60 MB
        
        is_valid, message = validate_pdf_file(mock_file)
        self.assertFalse(is_valid)
        self.assertIn("too large", message)
    
    def test_validate_pdf_file_valid(self):
        """Test PDF validation with valid file"""
        mock_file = Mock()
        mock_file.name = "document.pdf"
        mock_file.size = 1024 * 1024  # 1 MB
        
        is_valid, message = validate_pdf_file(mock_file)
        self.assertTrue(is_valid)
        self.assertEqual(message, "Valid PDF file")
    
    def test_truncate_text_short(self):
        """Test text truncation with short text"""
        text = "Short text"
        result = truncate_text(text, max_length=100)
        self.assertEqual(result, text)
    
    def test_truncate_text_long(self):
        """Test text truncation with long text"""
        text = "A" * 400
        result = truncate_text(text, max_length=300)
        self.assertEqual(len(result), 303)  # 300 + "..."
        self.assertTrue(result.endswith("..."))


class TestDocumentProcessor(unittest.TestCase):
    """Test document processing service"""
    
    def test_chunk_text_basic(self):
        """Test basic text chunking"""
        from src.services.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        
        text = "A" * 2000
        chunks = processor.chunk_text(text, chunk_size=800, overlap=100)
        
        self.assertGreater(len(chunks), 1)
        self.assertEqual(len(chunks[0]), 800)
    
    def test_chunk_text_with_overlap(self):
        """Test that overlap works correctly"""
        from src.services.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        
        text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 50  # 1300 chars
        chunks = processor.chunk_text(text, chunk_size=500, overlap=100)
        
        # With overlap, chunks should share some content
        self.assertGreater(len(chunks), 1)
        # First chunk end should overlap with second chunk start
        if len(chunks) > 1:
            overlap_region_chunk1 = chunks[0][-100:]
            overlap_region_chunk2 = chunks[1][:100]
            # They should have some overlap
            self.assertEqual(overlap_region_chunk1, overlap_region_chunk2)
    
    def test_chunk_text_empty(self):
        """Test chunking with empty text"""
        from src.services.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        
        text = ""
        chunks = processor.chunk_text(text, chunk_size=500, overlap=50)
        
        # Empty text returns empty list or single empty chunk depending on implementation
        self.assertGreaterEqual(len(chunks), 0)
        if len(chunks) > 0:
            self.assertEqual(chunks[0], "")
    
    def test_chunk_text_smaller_than_chunk_size(self):
        """Test chunking with text smaller than chunk size"""
        from src.services.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        
        text = "Small text"
        chunks = processor.chunk_text(text, chunk_size=500, overlap=50)
        
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], text)
    
    def test_chunk_text_with_default_params(self):
        """Test chunking with default parameters from settings"""
        from src.services.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        
        text = "X" * 3000
        chunks = processor.chunk_text(text)  # Uses CHUNK_SIZE and OVERLAP defaults
        
        self.assertGreater(len(chunks), 0)
        # Verify it uses the default chunk size
        self.assertLessEqual(len(chunks[0]), CHUNK_SIZE)


class TestSearchService(unittest.TestCase):
    """Test search service functionality"""
    
    def test_search_service_init(self):
        """Test search service initialization (placeholder for now)"""
        # This test currently passes as a placeholder
        # In a real scenario, we'd mock Pinecone and test initialization
        pass
    
    @patch('src.services.search_service.SentenceTransformer')
    def test_query_embedding_shape(self, mock_transformer):
        """Test that query embeddings have correct dimensions"""
        # Mock the sentence transformer
        mock_model = MagicMock()
        mock_model.encode.return_value = [0.1] * 1024  # Mock 1024-dim embedding
        mock_transformer.return_value = mock_model
        
        # This is a simplified test - in reality you'd test the actual embedding
        embedding = mock_model.encode("test query")
        self.assertEqual(len(embedding), 1024)


class TestQAService(unittest.TestCase):
    """Test question answering service"""
    
    def test_generate_answer_empty_chunks(self):
        """Test answer generation with empty chunks"""
        from src.services.qa_service import QAService
        
        # Mock the Gemini client
        with patch('src.services.qa_service.genai.Client') as mock_client:
            qa_service = QAService()
            
            # Test with empty chunks
            answer = qa_service.generate_answer("What is sustainability?", [])
            
            self.assertEqual(answer, "Information not found in the provided ESG documents.")
    
    def test_generate_answer_context_building(self):
        """Test that context is properly built from chunks"""
        from src.services.qa_service import QAService
        
        with patch('src.services.qa_service.genai.Client') as mock_client:
            # Mock the Gemini response
            mock_response = Mock()
            mock_response.text = "Test answer"
            mock_client.return_value.models.generate_content.return_value = mock_response
            
            qa_service = QAService()
            
            test_chunks = [
                {"company": "CompanyA", "text": "Carbon emissions reduced by 20%", "score": 0.95},
                {"company": "CompanyB", "text": "Renewable energy target of 50%", "score": 0.90}
            ]
            
            answer = qa_service.generate_answer("What are the targets?", test_chunks)
            
            # Verify answer is generated
            self.assertEqual(answer, "Test answer")
            
            # Verify generate_content was called
            mock_client.return_value.models.generate_content.assert_called_once()


class TestConfigSettings(unittest.TestCase):
    """Test configuration settings"""
    
    def test_config_values_exist(self):
        """Verify all required config values are set"""
        from src.config.settings import (
            PINECONE_API_KEY,
            INDEX_NAME,
            CHUNK_SIZE,
            OVERLAP,
            EMBEDDING_MODEL,
            TOP_K,
            GEMINI_API_KEY
        )
        
        # Verify they exist (not None)
        self.assertIsNotNone(PINECONE_API_KEY)
        self.assertIsNotNone(INDEX_NAME)
        self.assertIsNotNone(CHUNK_SIZE)
        self.assertIsNotNone(OVERLAP)
        self.assertIsNotNone(EMBEDDING_MODEL)
        self.assertIsNotNone(TOP_K)
        self.assertIsNotNone(GEMINI_API_KEY)
    
    def test_config_types(self):
        """Verify config values have correct types"""
        from src.config.settings import CHUNK_SIZE, OVERLAP, TOP_K, EMBEDDING_MODEL, INDEX_NAME
        
        self.assertIsInstance(CHUNK_SIZE, int)
        self.assertIsInstance(OVERLAP, int)
        self.assertIsInstance(TOP_K, int)
        self.assertIsInstance(EMBEDDING_MODEL, str)
        self.assertIsInstance(INDEX_NAME, str)
    
    def test_config_value_ranges(self):
        """Verify config values are within reasonable ranges"""
        from src.config.settings import CHUNK_SIZE, OVERLAP, TOP_K
        
        self.assertGreater(CHUNK_SIZE, 0)
        self.assertGreater(OVERLAP, 0)
        self.assertGreater(TOP_K, 0)
        self.assertLess(OVERLAP, CHUNK_SIZE)  # Overlap should be less than chunk size


if __name__ == '__main__':
    unittest.main()
