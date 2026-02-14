# tools/search/duckduckgo_search.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse, parse_qs, unquote


DUCKDUCKGO_SEARCH_URL = "https://html.duckduckgo.com/html/?q="


def extract_real_url(ddg_url: str) -> str | None:
    """
    Extract actual destination from DuckDuckGo redirect link.
    """
    if "uddg=" not in ddg_url:
        return None

    parsed = urlparse(ddg_url)
    query_params = parse_qs(parsed.query)

    if "uddg" in query_params:
        return unquote(query_params["uddg"][0])

    return None


def search_duckduckgo(query: str, max_results: int = 5):

    url = DUCKDUCKGO_SEARCH_URL + quote_plus(query)

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    results = []

    for a in soup.select("a.result__a"):
        href = a.get("href")
        if not href:
            continue

        real_url = extract_real_url(href)

        if real_url:
            results.append(real_url)

        if len(results) >= max_results:
            break

    return results
