"""
Helper utility functions for the ESG Question Answering System
"""

import os


def get_available_companies(data_folder: str) -> list:
    """
    Extract company names from PDF files in data folder
    
    Args:
        data_folder: Path to folder containing PDF files
        
    Returns:
        Sorted list of company names with "General" as first option
    """
    companies = ["General"]  # Default option for all companies
    
    if os.path.exists(data_folder):
        for file in os.listdir(data_folder):
            if file.lower().endswith(".pdf"):
                # Remove .pdf extension to get company name
                company_name = file.replace(".pdf", "")
                companies.append(company_name)
    
    return sorted(companies)


def validate_pdf_file(file) -> tuple:
    """
    Validate uploaded PDF file
    
    Args:
        file: Uploaded file object
        
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if file is None:
        return False, "No file uploaded"
    
    if not file.name.lower().endswith('.pdf'):
        return False, "File must be a PDF"
    
    # Check file size (max 50MB)
    max_size = 50 * 1024 * 1024  # 50MB in bytes
    if file.size > max_size:
        return False, f"File too large. Maximum size is 50MB"
    
    return True, "Valid PDF file"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def truncate_text(text: str, max_length: int = 300) -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Input text
        max_length: Maximum length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
