"""
Search Service
Handles semantic search functionality using vector embeddings
"""

from sentence_transformers import SentenceTransformer
from pinecone import Pinecone

from src.config.settings import (
    PINECONE_API_KEY,
    INDEX_NAME,
    TOP_K,
    EMBEDDING_MODEL
)


class SearchService:
    """Service for performing semantic search on vector database"""
    
    def __init__(self):
        """Initialize search service with model and Pinecone connection"""
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index = self.pc.Index(INDEX_NAME)
    
    def semantic_search(self, user_query: str, top_k: int = TOP_K, 
                       company_name: str = None) -> list:
        """
        Perform semantic search to find relevant document chunks
        
        Args:
            user_query: User's search query
            top_k: Number of top results to return
            company_name: Optional company filter (None or "General" for all)
            
        Returns:
            List of dictionaries containing search results with scores
        """
        # Convert query to vector embedding
        query_embedding = self.model.encode(user_query).tolist()
        
        # Build query parameters
        query_params = {
            "vector": query_embedding,
            "top_k": top_k,
            "include_metadata": True
        }
        
        # Add company filter if specified
        if company_name and company_name != "General":
            query_params["filter"] = {"company": {"$eq": company_name}}
        
        # Execute search
        results = self.index.query(**query_params)
        
        # Extract and format results
        retrieved_chunks = []
        for match in results["matches"]:
            retrieved_chunks.append({
                "score": match["score"],
                "company": match["metadata"].get("company"),
                "text": match["metadata"].get("text")
            })
        
        return retrieved_chunks


# Backward compatibility function
def semantic_search(user_query: str, model, index, top_k: int = TOP_K, 
                   company_name: str = None) -> list:
    """
    Legacy function for backward compatibility
    
    Args:
        user_query: User's search query
        model: Sentence transformer model  
        index: Pinecone index
        top_k: Number of results
        company_name: Optional company filter
        
    Returns:
        List of search results
    """
    query_embedding = model.encode(user_query).tolist()
    
    query_params = {
        "vector": query_embedding,
        "top_k": top_k,
        "include_metadata": True
    }
    
    if company_name and company_name != "General":
        query_params["filter"] = {"company": {"$eq": company_name}}
    
    results = index.query(**query_params)
    
    retrieved_chunks = []
    for match in results["matches"]:
        retrieved_chunks.append({
            "score": match["score"],
            "company": match["metadata"].get("company"),
            "text": match["metadata"].get("text")
        })
    
    return retrieved_chunks
