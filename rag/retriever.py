import sys
import os

# Add project root to python path for importing Config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from langchain_community.vectorstores import Chroma

def retrieve(query: str, k: int = 5, doc_type_filter: str = None) -> list:
    """
    Retrieves the most relevant chunks from ChromaDB for a given query.
    
    Args:
        query: The search query string.
        k: The number of results to return (default: 5).
        doc_type_filter: Optional document type to filter by (e.g. 'hdr', 'itu', 'sdg', 'worldbank').
        
    Returns:
        A list of dicts: {"text": str, "source": str, "page": int, "score": float}
    """
    persist_dir = Config.CHROMA_PERSIST_DIR
    collection_name = "sdg_policy_briefs"
    embeddings = Config.get_embeddings()
    
    # Initialize the vectorstore
    vectorstore = Chroma(
        persist_directory=persist_dir,
        collection_name=collection_name,
        embedding_function=embeddings
    )
    
    # Set search parameters
    search_kwargs = {}
    if doc_type_filter:
        search_kwargs["filter"] = {"doc_type": doc_type_filter}
        
    # Query the vectorstore. similarity_search_with_score returns tuples of (Document, score).
    # In Chroma, score is the distance (L2 distance), where a lower distance means higher similarity.
    results = vectorstore.similarity_search_with_score(query, k=k, **search_kwargs)
    
    retrieved_chunks = []
    for doc, score in results:
        retrieved_chunks.append({
            "text": doc.page_content,
            "source": doc.metadata.get("source_doc", "Unknown"),
            "page": doc.metadata.get("page_number", 0),
            "score": float(score)
        })
        
    return retrieved_chunks

if __name__ == "__main__":
    Config.validate()
    
    # Set up test query
    test_query = sys.argv[1] if len(sys.argv) > 1 else "What is the status of SDG target indicators?"
    print(f"Testing retriever with query: '{test_query}'")
    
    try:
        results = retrieve(test_query, k=3)
        if not results:
            print("No results returned. Ensure you have run ingest.py first to populate the vector store.")
        else:
            print(f"\nRetrieved {len(results)} chunks:")
            for idx, res in enumerate(results, 1):
                print(f"\n[{idx}] L2 Distance (Score): {res['score']:.4f}")
                print(f"Source: {res['source']} (Page {res['page']})")
                print(f"Content snippet: {res['text'][:250]}...")
    except Exception as e:
        print(f"Error during retrieval test: {e}")
