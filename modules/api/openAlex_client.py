# openAlex_client.py
# modules/api/openalex_client.py
import requests
from typing import List, Dict
from modules.preprocessing.extractor import reconstruct_abstract, clean_text

OPENALEX_BASE = "https://api.openalex.org"

def search_openalex(query: str, max_results: int = 5) -> List[Dict]:
    """Fetch papers from OpenAlex"""
    params = {
        "filter": f"display_name.search:{query}",
        "per-page": max_results,
        "sort": "relevance_score:desc"
    }

    try:
        resp = requests.get(f"{OPENALEX_BASE}/works", params=params, timeout=10)
        resp.raise_for_status()
        results = resp.json().get("results", [])
    except Exception:
        return []

    papers = []
    for item in results:
        title = item.get("title") or ""
        abs_text = reconstruct_abstract(item.get("abstract_inverted_index"))
        abs_text = clean_text(abs_text)  # clean thêm

        papers.append({
            "title": title,
            "abstract": abs_text,
            "year": item.get("publication_year", None),
            "citation": item.get("cited_by_count", 0),
            "id": item.get("id"),
            "doi": item.get("doi"),
            "source": "openalex",
            "query_used": query
        })

    return papers

