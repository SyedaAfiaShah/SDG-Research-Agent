import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    # ChromaDB Configuration
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "data/chromadb")
    
    # LLM Settings
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-pro")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
    
    # RAG Settings
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 800))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))
    MAX_RETRIEVAL_RESULTS = int(os.getenv("MAX_RETRIEVAL_RESULTS", 5))
    
    # Evaluation Settings
    EVALUATION_THRESHOLD = float(os.getenv("EVALUATION_THRESHOLD", 0.7))
    
    # Ingestion Settings
    INGEST_DEV_MODE = os.getenv("INGEST_DEV_MODE", "true").lower() == "true"

    @classmethod
    def get_llm(cls):
        """Returns the appropriate native CrewAI LLM instance based on provider."""
        from crewai import LLM
        if cls.LLM_PROVIDER == "openai":
            return LLM(model=cls.LLM_MODEL, api_key=cls.OPENAI_API_KEY, temperature=0.2)
        elif cls.LLM_PROVIDER == "gemini":
            # CrewAI native Gemini requires gemini/ prefix for Gemini models
            model_name = cls.LLM_MODEL
            if not model_name.startswith("gemini/"):
                model_name = f"gemini/{model_name}"
            return LLM(model=model_name, api_key=cls.GOOGLE_API_KEY, temperature=0.2)
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {cls.LLM_PROVIDER}")

    @classmethod
    def get_embeddings(cls):
        """Returns the appropriate LangChain embeddings class based on provider."""
        if cls.LLM_PROVIDER == "openai":
            from langchain_openai import OpenAIEmbeddings
            return OpenAIEmbeddings(model=cls.EMBEDDING_MODEL, openai_api_key=cls.OPENAI_API_KEY)
        elif cls.LLM_PROVIDER == "gemini":
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            return GoogleGenerativeAIEmbeddings(model=cls.EMBEDDING_MODEL, google_api_key=cls.GOOGLE_API_KEY)
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {cls.LLM_PROVIDER}")

    @classmethod
    def validate(cls):
        """Validates that keys are set depending on the selected provider."""
        if cls.LLM_PROVIDER == "openai":
            if not cls.OPENAI_API_KEY:
                raise ValueError("LLM_PROVIDER is set to 'openai', but OPENAI_API_KEY is not set.")
        elif cls.LLM_PROVIDER == "gemini":
            if not cls.GOOGLE_API_KEY:
                raise ValueError("LLM_PROVIDER is set to 'gemini', but GOOGLE_API_KEY / GEMINI_API_KEY is not set.")
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {cls.LLM_PROVIDER}. Must be 'openai' or 'gemini'.")

if __name__ == "__main__":
    print("=== Loading Configuration ===")
    try:
        Config.validate()
        print(f"LLM Provider: {Config.LLM_PROVIDER}")
        print(f"LLM Model: {Config.LLM_MODEL}")
        print(f"Embedding Model: {Config.EMBEDDING_MODEL}")
        print(f"ChromaDB Directory: {Config.CHROMA_PERSIST_DIR}")
        print(f"Chunk Size: {Config.CHUNK_SIZE}, Overlap: {Config.CHUNK_OVERLAP}")
        print(f"Max Retrieval Results: {Config.MAX_RETRIEVAL_RESULTS}")
        print(f"Evaluation Threshold Score: {Config.EVALUATION_THRESHOLD}")
        print("API Key Verification:")
        if Config.LLM_PROVIDER == "gemini":
            key = Config.GOOGLE_API_KEY
            masked = key[:4] + "..." + key[-4:] if key and len(key) > 8 else "None"
            print(f"  Google API Key: {masked} (Verified)")
        elif Config.LLM_PROVIDER == "openai":
            key = Config.OPENAI_API_KEY
            masked = key[:4] + "..." + key[-4:] if key and len(key) > 8 else "None"
            print(f"  OpenAI API Key: {masked} (Verified)")
        print("\nConfiguration loaded successfully.")
    except Exception as e:
        print(f"Error loading configuration: {e}")
