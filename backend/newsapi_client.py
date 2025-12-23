"""
NewsAPI.ai client (or compatible) for fetching news articles by query.
The API key is provided by the user (limited tokens); we keep calls minimal and handle errors gracefully.
"""
import os
from typing import List, Dict
import requests
from dotenv import load_dotenv

load_dotenv()

NEWSAPI_AI_KEY = (os.getenv("NEWSAPI_AI_KEY", "") or "").strip()
NEWSAPI_AI_BASE_URL = (os.getenv("NEWSAPI_AI_BASE_URL", "https://newsapi.ai/api/v1") or "").strip().rstrip("/")


def _get_headers() -> Dict[str, str]:
    if not NEWSAPI_AI_KEY:
        raise RuntimeError("NEWSAPI_AI_KEY is not configured")
    return {"x-api-key": NEWSAPI_AI_KEY}


def search_news_for_query(query: str, limit: int = 20) -> List[Dict]:
    """
    Search news for the given query. Keep requests minimal to respect token limits.
    """
    if not query:
        return []

    endpoint = f"{NEWSAPI_AI_BASE_URL}/search"
    params = {
        "q": query,
        "language": "en",
        "pageSize": min(limit, 50),
    }

    try:
        resp = requests.get(endpoint, headers=_get_headers(), params=params, timeout=15)
        if resp.status_code != 200:
            print(f"NewsAPI search failed {resp.status_code}: {resp.text[:200]}")
            return []
        data = resp.json() if resp.text else {}
    except Exception as exc:
        print(f"NewsAPI search error for '{query}': {exc}")
        return []

    # Expected structure may vary; handle common shapes
    articles = (
        data.get("articles", [])
        or data.get("results", [])
        or data.get("data", [])
        or (data if isinstance(data, list) else [])
    )

    cleaned: List[Dict] = []
    for item in articles:
        if not isinstance(item, dict):
            continue
        cleaned.append(
            {
                "ticker": query,
                "title": item.get("title", "") or item.get("headline", ""),
                "summary": item.get("description", item.get("summary", "")),
                "publisher": (
                    item.get("source", {}).get("name", "")
                    if isinstance(item.get("source"), dict)
                    else item.get("source", item.get("publisher", ""))
                ),
                "link": item.get("url", item.get("link", "")),
            }
        )

    return cleaned

