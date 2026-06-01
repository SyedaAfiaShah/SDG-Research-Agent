import sys
import os
import requests
import urllib.parse
from crewai.tools import tool

# Add project root to python path for importing Config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

@tool("AcademicSearch")
def semantic_scholar_tool(query: str) -> str:
    """
    Search academic papers on Semantic Scholar by query.
    
    Args:
        query: Academic research query string (e.g., 'digital inclusion rural development').
        
    Returns:
        A formatted string of the top 5 relevant papers including title, authors, year, and abstract snippet.
    """
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": 5,
        "fields": "title,authors,year,abstract"
    }
    
    # Headers to make request look like a browser and support optional API Key
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key
        
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        papers = data.get("data", [])
        if not papers:
            return f"No papers found for query: '{query}'."
            
        results = []
        for idx, paper in enumerate(papers, 1):
            title = paper.get("title", "No Title")
            year = paper.get("year", "N/A")
            authors_list = [a.get("name", "") for a in paper.get("authors", [])]
            authors = ", ".join(authors_list) if authors_list else "Unknown Authors"
            abstract = paper.get("abstract")
            abstract_snippet = abstract[:250] + "..." if abstract else "No abstract available"
            
            paper_info = (
                f"{idx}. {title} ({year})\n"
                f"   Authors: {authors}\n"
                f"   Summary: {abstract_snippet}"
            )
            results.append(paper_info)
            
        return f"Academic papers for query '{query}':\n\n" + "\n\n".join(results)
        
    except Exception as e:
        err_msg = str(e)
        # If rate limited (429 or Client Error), automatically query the live Crossref API
        if "429" in err_msg or "Too Many Requests" in err_msg or "Client Error" in err_msg:
            print(f"⚠️ Semantic Scholar Rate limit hit (429). Querying live Crossref API fallback...")
            return query_crossref(query)
        return f"Error searching academic literature: {e}"

def query_crossref(query: str) -> str:
    """
    Queries the open Crossref API for live academic papers as a fallback.
    """
    safe_query = urllib.parse.quote(query)
    url = f"https://api.crossref.org/works?query={safe_query}&rows=5"
    try:
        # Polite headers for Crossref
        headers = {
            "User-Agent": "SDGResearchAgent/1.0 (mailto:admin@sdg-agent.local)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        items = data.get("message", {}).get("items", [])
        if not items:
            return f"No papers found on Crossref for query: '{query}'."
            
        results = []
        for idx, item in enumerate(items, 1):
            titles = item.get("title", [])
            title = titles[0] if titles else "No Title"
            
            # Extract publication year
            published = item.get("published", {})
            date_parts = published.get("date-parts", [[]])[0]
            year = str(date_parts[0]) if date_parts else "N/A"
            
            # Extract authors
            authors_list = []
            for author in item.get("author", []):
                name = author.get("name")
                if not name:
                    name = f"{author.get('given', '')} {author.get('family', '')}".strip()
                if name:
                    authors_list.append(name)
            authors = ", ".join(authors_list) if authors_list else "Unknown Authors"
            
            # Extract container (journal/book title)
            container = item.get("container-title", [])
            container_title = container[0] if container else ""
            publisher = item.get("publisher", "Unknown Publisher")
            source_info = f"Published in: {container_title}" if container_title else f"Publisher: {publisher}"
            
            paper_info = (
                f"{idx}. {title} ({year}) [Crossref Search]\n"
                f"   Authors: {authors}\n"
                f"   Source: {source_info}"
            )
            results.append(paper_info)
            
        return f"Academic papers for query '{query}' (Live Crossref Search):\n\n" + "\n\n".join(results)
        
    except Exception as e:
        return f"Error searching Crossref fallback API: {e}"

if __name__ == "__main__":
    Config.validate()
    print("Testing AcademicSearch tool...")
    
    test_query = "digital divide rural Pakistan"
    result = semantic_scholar_tool.invoke({"query": test_query})
    print("\nResult:")
    print(result)
