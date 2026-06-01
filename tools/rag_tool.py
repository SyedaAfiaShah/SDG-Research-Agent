import sys
import os
from crewai.tools import tool

# Add project root to python path for importing Config and Retriever
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from rag.retriever import retrieve

@tool("KnowledgeBase")
def rag_tool(query: str) -> str:
    """
    Search UNDP reports, SDG documents, and development policy papers for relevant evidence.
    
    Args:
        query: Specific search query string regarding development, digital inclusion, or policy indicators.
        
    Returns:
        A formatted string combining top retrieved text chunks with source filenames and page numbers.
    """
    try:
        # Retrieve the top 5 chunks
        results = retrieve(query, k=5)
        if not results:
            return "No relevant documents or policy information found in the knowledge base."
            
        formatted_results = []
        for idx, res in enumerate(results, 1):
            source = res.get("source", "Unknown")
            page = res.get("page", "Unknown")
            score = res.get("score", 0.0)
            text = res.get("text", "").strip()
            
            # Format results nicely
            formatted_results.append(
                f"[Source {idx}]: {source} (Page {page}, L2 Distance: {score:.4f})\n"
                f"Content: {text}"
            )
            
        return "\n\n".join(formatted_results)
        
    except Exception as e:
        return f"Error querying local knowledge base: {e}"

if __name__ == "__main__":
    Config.validate()
    print("Testing KnowledgeBase (RAG) tool...")
    
    # Simple query test
    test_query = "What are the targets for digital transformation and internet access?"
    # Note: This will fail if ChromaDB isn't ingested yet, which is expected before running ingest.py
    try:
        result = rag_tool.invoke({"query": test_query})
        print("\nResult:")
        print(result)
    except Exception as e:
        print(f"\nResult: Retrieval failed (this is expected if you haven't run ingest.py yet).\nError details: {e}")
