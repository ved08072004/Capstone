"""
Unit and Integration Tests for ESG Question Answering System
"""

import unittest
from src.utils.helpers import get_available_companies, validate_pdf_file, format_file_size


class TestHelpers(unittest.TestCase):
    """Test utility helper functions"""
    
    def test_format_file_size(self):
        """Test file size formatting"""
        self.assertEqual(format_file_size(500), "500 B")
        self.assertEqual(format_file_size(1024), "1.00 KB")
        self.assertEqual(format_file_size(1048576), "1.00 MB")
    
    def test_get_available_companies(self):
        """Test company extraction"""
        companies = get_available_companies("./data/pdfs")
        self.assertIsInstance(companies, list)
        self.assertIn("General", companies)


class TestServices(unittest.TestCase):
    """Test service classes"""
    
    def test_search_service_init(self):
        """Test search service initialization"""
        # This would require mocking Pinecone and other dependencies
        pass
    
    def test_document_processor_chunk_text(self):
        """Test text chunking"""
        from src.services.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        
        text = "A" * 2000
        chunks = processor.chunk_text(text, chunk_size=800, overlap=100)
        
        self.assertGreater(len(chunks), 1)
        self.assertEqual(len(chunks[0]), 800)


if __name__ == '__main__':
    unittest.main()
