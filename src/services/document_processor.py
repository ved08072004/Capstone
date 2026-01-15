"""
Document Processing Service
Handles PDF text extraction, chunking, embedding generation, and vector storage
"""

import os
import pdfplumber
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone

from config.settings import (
    PINECONE_API_KEY,
    INDEX_NAME,
    CHUNK_SIZE,
    OVERLAP,
    EMBEDDING_MODEL
)


class DocumentProcessor:
    """Service for processing PDF documents and storing in vector database"""
    
    def __init__(self):
        """Initialize the document processor with model and Pinecone connection"""
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index = self.pc.Index(INDEX_NAME)
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as string
        """
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    
    def chunk_text(self, text: str, chunk_size: int = CHUNK_SIZE, 
                   overlap: int = OVERLAP) -> list:
        """
        Split text into overlapping chunks
        
        Args:
            text: Input text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Number of overlapping characters between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    def process_and_store_pdf(self, pdf_file, company_name: str = None) -> tuple:
        """
        Process PDF file and store vectors in Pinecone
        
        Args:
            pdf_file: PDF file object or path
            company_name: Name of the company (optional, extracted from filename) 
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Handle both file paths and uploaded file objects
            if hasattr(pdf_file, 'name'):
                # Streamlit uploaded file
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(pdf_file.getvalue())
                    pdf_path = tmp_file.name
                
                if company_name is None:
                    company_name = pdf_file.name.replace(".pdf", "")
            else:
                # File path
                pdf_path = pdf_file
                if company_name is None:
                    company_name = os.path.basename(pdf_file).replace(".pdf", "")
            
            # Extract text
            text = self.extract_text_from_pdf(pdf_path)
            
            if not text.strip():
                return False, "No text found in PDF"
            
            # Chunk text
            chunks = self.chunk_text(text)
            
            # Create embeddings
            embeddings = self.model.encode(chunks, show_progress_bar=False)
            
            # Prepare vectors for Pinecone
            vectors = []
            for i, emb in enumerate(embeddings):
                vectors.append((
                    f"{company_name}_{i}",
                    emb.tolist(),
                    {
                        "company": company_name,
                        "text": chunks[i]
                    }
                ))
            
            # Upsert into Pinecone
            self.index.upsert(vectors=vectors)
            
            # Clean up temporary file if created
            if hasattr(pdf_file, 'name') and os.path.exists(pdf_path):
                os.remove(pdf_path)
            
            return True, f"Successfully processed {len(chunks)} chunks from {company_name}"
        
        except Exception as e:
            return False, f"Error processing PDF: {str(e)}"
    
    def process_folder(self, folder_path: str) -> dict:
        """
        Process all PDF files in a folder
        
        Args:
            folder_path: Path to folder containing PDFs
            
        Returns:
            Dictionary with processing results
        """
        results = {
            "total_files": 0,
            "successful": 0,
            "failed": 0,
            "total_chunks": 0
        }
        
        if not os.path.exists(folder_path):
            return results
        
        for file in os.listdir(folder_path):
            if not file.lower().endswith(".pdf"):
                continue
            
            results["total_files"] += 1
            pdf_path = os.path.join(folder_path, file)
            company_name = file.replace(".pdf", "")
            
            success, message = self.process_and_store_pdf(pdf_path, company_name)
            
            if success:
                results["successful"] += 1
                # Extract number of chunks from message
                chunks_count = int(message.split()[2])
                results["total_chunks"] += chunks_count
            else:
                results["failed"] += 1
        
        return results
