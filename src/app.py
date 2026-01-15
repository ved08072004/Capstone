"""
ESG Question Answering System - Streamlit Application
Main entry point for the web interface
"""

import streamlit as st
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from google import genai

# Import from package structure (relative imports)
from config.settings import (
    PINECONE_API_KEY,
    GEMINI_API_KEY,
    INDEX_NAME,
    TOP_K,
    DATA_FOLDER,
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT
)
from services.document_processor import DocumentProcessor
from services.search_service import semantic_search
from services.qa_service import generate_answer_with_gemini
from utils.helpers import get_available_companies

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)

# ---------------------------
# CUSTOM CSS
# ---------------------------
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #10b981;
        --secondary-color: #059669;
        --background-color: #0f172a;
        --card-background: #1e293b;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: #e0f2fe;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Card styling */
    .result-card {
        background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid #10b981;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .result-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3);
    }
    
    .answer-card {
        background: linear-gradient(145deg, #10b981 0%, #059669 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
        border: 2px solid #34d399;
    }
    
    .answer-card h3 {
        color: white;
        margin-top: 0;
        font-size: 1.4rem;
    }
    
    .answer-card p {
        color: #f0fdf4;
        font-size: 1.1rem;
        line-height: 1.7;
    }
    
    /* Score badge */
    .score-badge {
        display: inline-block;
        background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
    }
    
    /* Company tag */
    .company-tag {
        display: inline-block;
        background: #475569;
        color: #e2e8f0;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        margin-left: 0.5rem;
    }
    
    /* Upload section */
    .upload-section {
        background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        border: 2px dashed #10b981;
    }
    
    /* Success/Error messages */
    .success-message {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .error-message {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    /* Sidebar styling */
    .sidebar-info {
        background: #1e293b;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 3px solid #10b981;
    }
    
    /* Spinner customization */
    div.stSpinner > div {
        border-top-color: #10b981 !important;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# INITIALIZE SESSION STATE
# ---------------------------
if 'embedder' not in st.session_state:
    with st.spinner("🔄 Loading embedding model..."):
        st.session_state.embedder = SentenceTransformer("intfloat/e5-large-v2")

if 'pinecone_index' not in st.session_state:
    with st.spinner("🔄 Connecting to Pinecone..."):
        pc = Pinecone(api_key=PINECONE_API_KEY)
        st.session_state.pinecone_index = pc.Index(INDEX_NAME)

if 'gemini_client' not in st.session_state:
    st.session_state.gemini_client = genai.Client(api_key=GEMINI_API_KEY)

if 'document_processor' not in st.session_state:
    st.session_state.document_processor = DocumentProcessor()

# ---------------------------
# MAIN APP UI
# ---------------------------
# Header
st.markdown("""
<div class="main-header">
    <h1>🌱 ESG Question Answering System</h1>
    <p>AI-Powered Sustainability Insights from ESG Documents</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📚 About")
    st.markdown("""
    <div class="sidebar-info">
        This system uses advanced AI to answer questions about Environmental, Social, and Governance (ESG) practices based on company documents.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⚙️ How it works")
    st.markdown("""
    1. **Upload** ESG documents (PDFs)
    2. **Ask** questions about sustainability practices
    3. **Get** AI-powered answers with source citations
    """)
    
    st.markdown("### 🔧 System Status")
    st.success("✅ Embedding Model Loaded")
    st.success("✅ Pinecone Connected")
    st.success("✅ Gemini AI Ready")

# Main content area
tab1, tab2 = st.tabs(["🔍 Ask Questions", "📤 Upload Documents"])

# TAB 1: Ask Questions
with tab1:
    st.markdown("### Ask Your ESG Question")
    
    # Company filter dropdown
    col_filter1, col_filter2 = st.columns([1, 2])
    with col_filter1:
        available_companies = get_available_companies(DATA_FOLDER)
        selected_company = st.selectbox(
            "🏢 Filter by Company:",
            options=available_companies,
            index=0,  # Default to "General"
            help="Select a specific company or 'General' to search all companies"
        )
    
    query = st.text_area(
        "Enter your question:",
        placeholder="e.g., What are the carbon emission reduction targets?",
        height=100,
        key="query_input"
    )
    
    # Show active filter status
    if selected_company != "General":
        st.info(f"🔍 Searching only within **{selected_company}** documents")
    else:
        st.info(f"🔍 Searching across **all companies**")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        search_button = st.button("🔍 Search & Answer", use_container_width=True)
    
    if search_button and query.strip():
        with st.spinner("🔎 Searching through ESG documents..."):
            try:
                # Perform semantic search with company filter
                top_chunks = semantic_search(
                    query,
                    st.session_state.embedder,
                    st.session_state.pinecone_index,
                    top_k=TOP_K,
                    company_name=selected_company
                )
                
                if top_chunks:
                    # Display top 3 results
                    st.markdown("### 📊 Top 3 Relevant Sources")
                    
                    for i, result in enumerate(top_chunks, 1):
                        st.markdown(f"""
                        <div class="result-card">
                            <h4>📄 Result {i}</h4>
                            <span class="score-badge">Relevance: {result['score']:.2%}</span>
                            <span class="company-tag">🏢 {result['company']}</span>
                            <p style="margin-top: 1rem; color: #e2e8f0; line-height: 1.6;">
                                {result['text'][:300]}{'...' if len(result['text']) > 300 else ''}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Generate AI answer
                    with st.spinner("🤖 Generating AI-powered answer..."):
                        answer = generate_answer_with_gemini(
                            query,
                            top_chunks,
                            st.session_state.gemini_client
                        )
                        
                        st.markdown(f"""
                        <div class="answer-card">
                            <h3>💡 AI-Generated Answer</h3>
                            <p>{answer}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ No relevant information found. Try rephrasing your question or upload more documents.")
            
            except Exception as e:
                st.markdown(f"""
                <div class="error-message">
                    ❌ Error: {str(e)}
                </div>
                """, unsafe_allow_html=True)
    
    elif search_button:
        st.warning("⚠️ Please enter a question first!")

# TAB 2: Upload Documents
with tab2:
    st.markdown("### Upload New ESG Documents")
    
    st.markdown("""
    <div class="upload-section">
        <p style="text-align: center; color: #e2e8f0; margin-bottom: 1rem;">
            📁 Upload PDF files containing ESG reports, sustainability documents, or corporate responsibility statements
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload ESG documents in PDF format"
    )
    
    if uploaded_file is not None:
        st.info(f"📄 Selected: **{uploaded_file.name}** ({uploaded_file.size / 1024:.2f} KB)")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            process_button = st.button("🚀 Process & Store", use_container_width=True)
        
        if process_button:
            with st.spinner("⚙️ Processing document... This may take a moment."):
                success, message = st.session_state.document_processor.process_and_store_pdf(
                    uploaded_file
                )
                
                if success:
                    st.markdown(f"""
                    <div class="success-message">
                        ✅ {message}
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.markdown(f"""
                    <div class="error-message">
                        ❌ {message}
                    </div>
                    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #94a3b8; padding: 1rem;">
    <p>🌍 Powered by Sentence Transformers, Pinecone Vector Database & Google Gemini AI</p>
</div>
""", unsafe_allow_html=True)
