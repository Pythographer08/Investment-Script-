"""
NewsAPI.ai client (or compatible) for fetching news articles by query.
The API key is provided by the user (limited tokens); we keep calls minimal and handle errors gracefully.
"""
import os
from typing import List, Dict
import requests
from dotenv import load_dotenv

load_dotenv()

# Event Registry / NewsAPI.ai style config
NEWSAPI_AI_KEY = (os.getenv("NEWSAPI_AI_KEY", "") or "").strip()
# Base URL points to Event Registry article API by default
NEWSAPI_AI_BASE_URL = (
    os.getenv("NEWSAPI_AI_BASE_URL", "https://eventregistry.org/api/v1") or ""
).strip().rstrip("/")


def search_news_for_query(query: str, limit: int = 20) -> List[Dict]:
    """
    Search news for the given query. Keep requests minimal to respect token limits.
    """
    if not query:
        return []

    if not NEWSAPI_AI_KEY:
        print("NEWSAPI_AI_KEY not configured; skipping news fetch")
        return []

    endpoint = f"{NEWSAPI_AI_BASE_URL}/article/getArticles"

    # Build minimal Event Registry / NewsAPI.ai style request body.
    # See: https://eventregistry.org/documentation (Get articles)
    payload = {
        "action": "getArticles",
        "keyword": query,
        "keywordLoc": "title,body",
        "articlesPage": 1,
        "articlesCount": min(limit, 20),
        "articlesSortBy": "date",
        "articlesSortByAsc": False,
        "dataType": ["news"],
        "resultType": "articles",
        # Limit to recent window to keep responses small
        "forceMaxDataTimeWindow": 7,
        "apiKey": NEWSAPI_AI_KEY,
    }

    try:
        resp = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        if resp.status_code != 200:
            print(f"NewsAPI search failed {resp.status_code}: {resp.text[:200]}")
            return []
        data = resp.json() if resp.text else {}
    except Exception as exc:
        print(f"NewsAPI search error for '{query}': {exc}")
        return []

    # For resultType='articles', Event Registry returns:
    # { "articles": { "results": [ ... ] } }
    articles_container = data.get("articles", {})
    articles = (
        articles_container.get("results", [])
        or data.get("results", [])
        or data.get("articles", [])
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

