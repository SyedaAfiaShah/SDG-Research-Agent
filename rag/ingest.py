import os
import sys
import glob
import chromadb

# Add project root to python path for importing Config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from rag.utils import get_doc_type, clean_text
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

def ingest_documents():
    # 1. Initialize local chromadb client to check if collection exists and has documents
    persist_dir = Config.CHROMA_PERSIST_DIR
    collection_name = "sdg_policy_briefs"
    
    # We use the chromadb persistent client directly to check if it's already populated
    client = chromadb.PersistentClient(path=persist_dir)
    
    # Check if collection exists and has items
    try:
        collection = client.get_collection(collection_name)
        count = collection.count()
        if count > 0:
            print("Knowledge base already loaded.")
            return
    except Exception:
        # Collection does not exist yet or is empty
        pass
        
    print("Initializing knowledge base ingestion...")
    
    # 2. Find all PDF files in data/documents
    docs_dir = os.path.join("data", "documents")
    pdf_pattern = os.path.join(docs_dir, "*.pdf")
    pdf_files = glob.glob(pdf_pattern)
    
    if not pdf_files:
        print(f"No PDF files found in {docs_dir}. Please place documents there before running.")
        return
        
    print(f"Found {len(pdf_files)} PDF documents to ingest.")
    
    all_chunks = []
    doc_chunk_counts = {}
    
    # Initialize splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP
    )
    
    # 3. Load and split each PDF
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        doc_type = get_doc_type(filename)
        print(f"Processing: {filename} (type: {doc_type})...")
        
        try:
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            
            # Dev mode page limiter to prevent rate limit limits
            if Config.INGEST_DEV_MODE and len(pages) > 15:
                print(f"  [Dev Mode] Limiting {filename} to first 15 pages (originally {len(pages)} pages).")
                pages = pages[:15]
            
            # Clean page contents and prepare chunks
            pdf_chunks = []
            for page in pages:
                page_content_cleaned = clean_text(page.page_content)
                # Skip page if it's empty after cleaning
                if not page_content_cleaned:
                    continue
                # Split page content
                page_chunks = splitter.split_text(page_content_cleaned)
                
                for chunk_text in page_chunks:
                    doc_chunk = Document(
                        page_content=chunk_text,
                        metadata={
                            "source_doc": filename,
                            "page_number": page.metadata.get("page", 0) + 1,  # Make page number 1-indexed
                            "doc_type": doc_type
                        }
                    )
                    pdf_chunks.append(doc_chunk)
            
            all_chunks.extend(pdf_chunks)
            doc_chunk_counts[filename] = len(pdf_chunks)
            print(f"  Split into {len(pdf_chunks)} chunks.")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            
    if not all_chunks:
        print("No content could be extracted or chunked. Ingestion aborted.")
        return
        
    print(f"Total chunks extracted across all documents: {len(all_chunks)}")
    
    # 4. Generate embeddings and store in ChromaDB with rate-limiting
    print("Generating embeddings and saving to ChromaDB with rate-limiting...")
    embeddings = Config.get_embeddings()
    
    # Initialize the Chroma store empty first
    vectorstore = Chroma(
        persist_directory=persist_dir,
        collection_name=collection_name,
        embedding_function=embeddings
    )
    
    import time
    batch_size = 40  # 40 chunks per batch. Fits perfectly in the 100 requests per minute quota.
    total_chunks = len(all_chunks)
    
    print(f"Adding documents in batches of {batch_size} with automatic 429 rate-limit handling...")
    for i in range(0, total_chunks, batch_size):
        batch = all_chunks[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (total_chunks + batch_size - 1) // batch_size
        
        # Retry loop for rate limits
        retries = 5
        while retries > 0:
            try:
                print(f"Ingesting batch {batch_num}/{total_batches} (chunks {i} to {min(i + batch_size, total_chunks)})...")
                vectorstore.add_documents(batch)
                break  # Success! Exit the retry loop.
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                    retries -= 1
                    sleep_time = 45
                    print(f"⚠️ Rate limit hit (429 / RESOURCE_EXHAUSTED).")
                    print(f"   Sleeping for {sleep_time} seconds to let the quota reset... ({retries} retries remaining)")
                    time.sleep(sleep_time)
                else:
                    # If it's a different error, raise it immediately
                    raise e
        else:
            raise RuntimeError(f"Failed to ingest batch {batch_num} after multiple retries due to rate limits.")
        
        # Sleep to stay well below the 100 RPM limit (40 requests every 35 seconds = 68 requests per minute)
        if i + batch_size < total_chunks:
            time.sleep(35.0)
            
    # For older versions of LangChain Chroma, call persist to flush to disk
    if hasattr(vectorstore, "persist"):
        vectorstore.persist()
        
    print("\n=== Ingestion Summary ===")
    print(f"Total chunks stored: {len(all_chunks)}")
    for doc, count in doc_chunk_counts.items():
        print(f" - {doc}: {count} chunks")
    print("Knowledge base successfully loaded.")

if __name__ == "__main__":
    Config.validate()
    ingest_documents()
