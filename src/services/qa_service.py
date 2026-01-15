"""
Question Answering Service
Generates AI-powered answers using LLM based on retrieved context
"""

from google import genai

from config.settings import GEMINI_API_KEY, LLM_MODEL


class QAService:
    """Service for generating answers using LLM"""
    
    def __init__(self):
        """Initialize QA service with Gemini client"""
        self.client = genai.Client(api_key=GEMINI_API_KEY)
    
    def generate_answer(self, user_query: str, top_chunks: list) -> str:
        """
        Generate detailed answer using Gemini based on retrieved chunks
        
        Args:
            user_query: User's question
            top_chunks: List of relevant document chunks from search
            
        Returns:
            Generated answer as string
        """
        if not top_chunks:
            return "Information not found in the provided ESG documents."
        
        # Prepare context from chunks
        context = "\n\n".join([
            f"Source {i+1} (Company: {c['company']}):\n{c['text']}"
            for i, c in enumerate(top_chunks)
        ])
        
        # Create detailed prompt
        prompt = f"""
You are a Sustainability ESG Analyst providing detailed, comprehensive insights.

CRITICAL REQUIREMENTS:
- Provide a DETAILED, COMPREHENSIVE answer between 200-400 words
- Answer ONLY using the sources provided below
- Do NOT use outside knowledge or make assumptions
- Structure your response with clear paragraphs covering different aspects
- Include specific details, numbers, targets, and timelines from the sources
- Explain the context, implications, and significance of the findings
- If the answer is not clearly present in sources, say: "Information not found in the provided ESG documents."

RESPONSE STRUCTURE:
1. Start with a direct answer to the question
2. Provide detailed explanation with specific data points from sources
3. Include relevant context about targets, timelines, and methodologies
4. Discuss implications or significance where relevant
5. Cite which companies the information comes from

SOURCES:
{context}

USER QUESTION:
{user_query}

DETAILED ANSWER (200-400 words, professional, well-structured paragraphs):
"""
        
        # Generate answer using Gemini
        response = self.client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt
        )
        
        return response.text.strip()
    
    def ask_question(self, user_query: str, search_service) -> tuple:
        """
        Complete QA pipeline: search + answer generation
        
        Args:
            user_query: User's question
            search_service: Instance of SearchService
            
        Returns:
            Tuple of (top_chunks, answer)
        """
        # Get relevant chunks
        top_chunks = search_service.semantic_search(user_query)
        
        # Generate answer
        answer = self.generate_answer(user_query, top_chunks)
        
        return top_chunks, answer


# Backward compatibility function
def generate_answer_with_gemini(user_query: str, top_chunks: list, client) -> str:
    """
    Legacy function for backward compatibility
    
    Args:
        user_query: User's question
        top_chunks: Retrieved document chunks
        client: Gemini client
        
    Returns:
        Generated answer
    """
    if not top_chunks:
        return "Information not found in the provided ESG documents."
    
    context = "\n\n".join([
        f"Source {i+1} (Company: {c['company']}):\n{c['text']}"
        for i, c in enumerate(top_chunks)
    ])
    
    prompt = f"""
You are a Sustainability ESG Analyst providing detailed, comprehensive insights.

CRITICAL REQUIREMENTS:
- Provide a DETAILED, COMPREHENSIVE answer between 200-400 words
- Answer ONLY using the sources provided below
- Do NOT use outside knowledge or make assumptions
- Structure your response with clear paragraphs covering different aspects
- Include specific details, numbers, targets, and timelines from the sources
- Explain the context, implications, and significance of the findings
- If the answer is not clearly present in sources, say: "Information not found in the provided ESG documents."

RESPONSE STRUCTURE:
1. Start with a direct answer to the question
2. Provide detailed explanation with specific data points from sources
3. Include relevant context about targets, timelines, and methodologies
4. Discuss implications or significance where relevant
5. Cite which companies the information comes from

SOURCES:
{context}

USER QUESTION:
{user_query}

DETAILED ANSWER (200-400 words, professional, well-structured paragraphs):
"""
    
    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt
    )
    return response.text.strip()
