"""
Query CLI Script
Command-line interface for asking ESG questions
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now we can import from src
from src.services.search_service import SearchService
from src.services.qa_service import QAService
from src.config.settings import TOP_K


def main():
    """Main function for interactive CLI query interface"""
    print("=" * 60)
    print("ESG QUESTION ANSWERING SYSTEM - CLI")
    print("=" * 60)
    print("\n[*] Loading services...")
    
    # Initialize services
    search_service = SearchService()
    qa_service = QAService()
    
    print("[✓] System ready!")
    print("\n[i] Type your ESG-related questions below.")
    print("    Type 'quit', 'exit', or 'q' to stop.\n")
    
    try:
        while True:
            # Get user input
            user_query = input("[?] Your question: ").strip()
            
            # Check for exit commands
            if user_query.lower() in ['quit', 'exit', 'q']:
                print("\n[+] Goodbye!")
                break
            
            # Skip empty queries
            if not user_query:
                print("[!] Please enter a question.\n")
                continue
            
            # Process the question
            print(f"\n[*] Searching for relevant information...")
            
            try:
                # Get relevant chunks
                top_chunks = search_service.semantic_search(user_query, top_k=TOP_K)
                
                if not top_chunks:
                    print("[!] No relevant information found.\n")
                    continue
                
                # Display top results
                print(f"\n[✓] Found {len(top_chunks)} relevant sources:\n")
                for i, chunk in enumerate(top_chunks, 1):
                    print(f"  [{i}] {chunk['company']} (Score: {chunk['score']:.2%})")
                    print(f"      {chunk['text'][:100]}...\n")
                
                # Generate answer
                print("[*] Generating AI answer...\n")
                answer = qa_service.generate_answer(user_query, top_chunks)
                
                print("[>] ANSWER:")
                print("-" * 60)
                print(answer)
                print("-" * 60 + "\n")
                
            except Exception as e:
                print(f"\n[x] Error: {e}\n")
    
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user. Ex iting...")
        print("[+] Goodbye!")


if __name__ == "__main__":
    main()
