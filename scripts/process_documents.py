"""
Process Documents Script
Standalone script for bulk processing PDF documents into the vector database
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now we can import from src
from src.services.document_processor import DocumentProcessor
from src.config.settings import DATA_FOLDER


def main():
    """Main function to process all PDFs in data folder"""
    print("=" * 60)
    print("ESG DOCUMENT PROCESSING SCRIPT")
    print("=" * 60)
    print(f"\n[*] Initializing document processor...")
    
    processor = DocumentProcessor()
    
    print(f"[*] Processing PDFs from: {DATA_FOLDER}")
    print(f"[*] Please wait...\n")
    
    results = processor.process_folder(DATA_FOLDER)
    
    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE!")
    print("=" * 60)
    print(f"Total files found: {results['total_files']}")
    print(f"Successfully processed: {results['successful']}")
    print(f"Failed: {results['failed']}")
    print(f"Total chunks stored: {results['total_chunks']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
