"""
Configuration management for ESG Question Answering System
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ---------------------------
# API Credentials
# ---------------------------
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ---------------------------
# Database Configuration  
# ---------------------------
INDEX_NAME = "capstone"

# ---------------------------
# Search Configuration
# ---------------------------
TOP_K = 3  # Number of top results to retrieve

# ---------------------------
# Document Processing Configuration
# ---------------------------
CHUNK_SIZE = 800  # Characters per chunk
OVERLAP = 100     # Overlap between chunks

# ---------------------------
# Model Configuration
# ---------------------------
EMBEDDING_MODEL = "intfloat/e5-large-v2"  # Sentence transformer model
LLM_MODEL = "gemini-2.0-flash-exp"        # Gemini model

# ---------------------------
# Paths Configuration
# ---------------------------
DATA_FOLDER = r"D:\Project\Capestone\data\pdfs"  # PDF documents location

# ---------------------------
# UI Configuration
# ---------------------------
PAGE_TITLE = "ESG Question Answering System"
PAGE_ICON = "🌱"
LAYOUT = "wide"
