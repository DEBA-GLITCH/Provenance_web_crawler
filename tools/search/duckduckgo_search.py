# tools/search/duckduckgo_search.py

from duckduckgo_search import DDGS
from itertools import islice

def search_duckduckgo(query: str, max_results: int = 5):
    """
    Search using the duckduckgo-search library for robust results.
    """
    results = []
    
    try:
        with DDGS() as ddgs:
            # text() returns a generator
            ddg_gen = ddgs.text(query, max_results=max_results)
            
            for r in ddg_gen:
                if "href" in r:
                    results.append(r["href"])
                    
    except Exception as e:
        print(f"⚠️ Search error: {e}")
        return []

    return results
