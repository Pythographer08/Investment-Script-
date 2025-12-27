from typing import List, Dict, Optional
import time

import datetime as dt

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from textblob import TextBlob
import yfinance as yf

# Import US and Indian tickers
from backend.us_tickers import US_TICKERS
from backend.indian_tickers import INDIAN_TICKERS

# Ticker universe: Combine US and Indian stocks
TICKERS: List[str] = US_TICKERS + INDIAN_TICKERS

# Simple in-memory cache with TTL (Time-To-Live)
_cache: Dict[str, tuple] = {}  # key -> (data, timestamp)
CACHE_TTL = 300  # 5 minutes in seconds


def _get_cache(key: str) -> Optional[any]:
    """Get cached data if still valid."""
    if key not in _cache:
        return None
    data, timestamp = _cache[key]
    if time.time() - timestamp > CACHE_TTL:
        del _cache[key]
        return None
    return data


def _set_cache(key: str, data: any) -> None:
    """Store data in cache with current timestamp."""
    _cache[key] = (data, time.time())


app = FastAPI(title="US & Indian Market Investment Recommendation API (Yahoo Finance)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _fetch_news_for_ticker(ticker: str) -> List[Dict]:
    """
    Fetch latest news for a single ticker using yfinance.
    yfinance v0.2+ uses nested structure: item['content']['title'], item['content']['summary']
    """
    try:
        t = yf.Ticker(ticker)
        # yfinance .news is a list of dicts with 'id' and 'content' keys
        news_items = t.news or []

        cleaned: List[Dict] = []
        for item in news_items:
            content = item.get("content", {})
            provider = content.get("provider", {})
            canonical = content.get("canonicalUrl", {})
            
            cleaned.append(
                {
                    "ticker": ticker,
                    "title": content.get("title", ""),
                    "summary": content.get("summary", "") or content.get("description", ""),
                    "publisher": provider.get("displayName", "") if isinstance(provider, dict) else "",
                    "link": canonical.get("url", "") if isinstance(canonical, dict) else content.get("link", ""),
                }
            )
        return cleaned
    except Exception as e:
        print(f"Error fetching news for {ticker}: {e}")
        return []


def _analyze_sentiment(text: str) -> Dict[str, float]:
    """
    Simple TextBlob polarity / subjectivity helper.
    Returns 0.0 for empty/whitespace-only text.
    """
    text = (text or "").strip()
    if not text:
        return {"polarity": 0.0, "subjectivity": 0.0}
    blob = TextBlob(text)
    return {
        "polarity": float(blob.sentiment.polarity),
        "subjectivity": float(blob.sentiment.subjectivity),
    }


def _recommendation_from_score(score: float) -> str:
    """
    Turn an average polarity score into Buy / Hold / Sell.
    Tunable thresholds.
    """
    if score >= 0.10:
        return "Buy"
    if score <= -0.05:
        return "Sell"
    return "Hold"


@app.get("/price_chart")
def price_chart(ticker: str):
    if ticker not in TICKERS:
        raise HTTPException(status_code=400, detail="Unsupported ticker")

    try:
        data = yf.Ticker(ticker).history(period="1mo")
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc))

    if data.empty:
        raise HTTPException(status_code=404, detail="No price data found")

    dates: List[str] = [d.strftime("%Y-%m-%d") for d in data.index.to_pydatetime()]
    closes: List[float] = [float(c) for c in data["Close"].tolist()]
    return {"ticker": ticker, "dates": dates, "closes": closes}


@app.get("/news")
def news():
    """
    Raw news feed for all tickers.
    Cached for 5 minutes to reduce API calls.
    """
    cache_key = "news_all"
    cached = _get_cache(cache_key)
    if cached is not None:
        return cached
    
    all_news: List[Dict] = []
    for ticker in TICKERS:
        try:
            all_news.extend(_fetch_news_for_ticker(ticker))
        except Exception:
            # If one ticker fails, continue with others
            continue
    
    _set_cache(cache_key, all_news)
    return all_news


@app.get("/sentiment")
def sentiment():
    """
    Per‑article sentiment for all news.
    Analyzes both title and summary together for better sentiment detection.
    Cached for 5 minutes to reduce computation.
    """
    cache_key = "sentiment_all"
    cached = _get_cache(cache_key)
    if cached is not None:
        return cached
    
    items = news()
    results: List[Dict] = []
    for n in items:
        title = n.get("title", "")
        summary = n.get("summary", "")
        # Combine title + summary for richer sentiment analysis
        combined_text = f"{title} {summary}".strip()
        scores = _analyze_sentiment(combined_text)
        results.append(
            {
                "ticker": n.get("ticker"),
                "title": title,
                "summary": summary or title,  # Fallback to title if no summary
                "polarity": scores["polarity"],
                "subjectivity": scores["subjectivity"],
            }
        )
    
    _set_cache(cache_key, results)
    return results


@app.get("/recommendations")
def recommendations():
    """
    Aggregate sentiment into per‑ticker recommendations.
    Enhanced with MCP technical indicators and fundamentals when available.
    Returns: ticker, avg_polarity, recommendation, confidence, factors, news_count.
    """
    sentiments = sentiment()
    if not sentiments:
        return []

    by_ticker: Dict[str, List[float]] = {}
    for item in sentiments:
        t = item["ticker"]
        by_ticker.setdefault(t, []).append(float(item["polarity"]))

    output: List[Dict] = []
    for ticker, scores in by_ticker.items():
        if not scores:
            continue
        avg_sentiment = sum(scores) / len(scores)
        news_count = len(scores)  # Count of news articles analyzed
        base_rec = _recommendation_from_score(avg_sentiment)
        
        # Try to enhance with MCP data (may not work for all Indian stocks)
        enhanced = _enhance_recommendation_with_mcp(ticker, avg_sentiment, base_rec)
        # Add news_count to the enhanced recommendation
        enhanced["news_count"] = news_count
        
        output.append(enhanced)

    # Stable ordering like the frontend's list
    ticker_to_row = {row["ticker"]: row for row in output}
    ordered: List[Dict] = []
    for t in TICKERS:
        row = ticker_to_row.get(t)
        if row:
            ordered.append(row)

    return ordered


def _enhance_recommendation_with_mcp(ticker: str, sentiment_score: float, base_rec: str) -> Dict:
    """
    Enhance recommendation using MCP tools (technical indicators, fundamentals).
    Falls back gracefully if MCP data unavailable.
    
    NOTE: Technical indicators are currently disabled to avoid timeouts.
    They can be enabled per-ticker via a separate endpoint if needed.
    """
    from backend.mcp_integration import get_technical_indicators, get_fundamental_snapshot
    
    factors = {"sentiment": sentiment_score}
    confidence = 0.5  # Base confidence from sentiment only
    
    # Skip technical indicators for now to avoid timeouts (109 stocks × API calls = too slow)
    # Technical indicators can be fetched on-demand via a separate endpoint if needed
    # Only fetch for US stocks if we want to enable it selectively
    # try:
    #     technicals = get_technical_indicators(ticker, period="6mo")
    #     ...
    # except Exception:
    #     pass
    
    # Skip fundamentals for now to avoid timeouts
    # try:
    #     fundamentals = get_fundamental_snapshot(ticker)
    #     ...
    # except Exception:
    #     pass
    
    # Final recommendation: combine sentiment + technicals
    final_rec = base_rec
    if "technical" in factors:
        rsi = factors["technical"].get("rsi")
        if rsi:
            if rsi < 30 and base_rec == "Hold":  # Oversold + neutral sentiment = Buy
                final_rec = "Buy"
                confidence += 0.1
            elif rsi > 70 and base_rec == "Buy":  # Overbought + positive sentiment = Hold
                final_rec = "Hold"
                confidence -= 0.1
    
    confidence = max(0.3, min(1.0, confidence))  # Clamp between 0.3 and 1.0
    
    return {
        "ticker": ticker,
        "avg_polarity": sentiment_score,
        "recommendation": final_rec,
        "confidence": round(confidence, 2),
        "factors": factors,
    }


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "US & Indian Market Investment Recommendation API (all data via Yahoo Finance)",
    }


@app.get("/health")
def health():
    """
    Health check endpoint for Render deployment.
    Returns immediately without any data fetching.
    """
    return {"status": "healthy", "service": "investment-recommendation-api"}


@app.get("/run-daily-report")
def run_daily_report():
    """
    Endpoint to trigger daily report generation (for cloud cron jobs).
    Returns success on 200; raises HTTPException with 500 on error.
    """
    try:
        # Import here to avoid circular imports
        import subprocess
        import sys
        from pathlib import Path

        script_path = Path(__file__).parent.parent / "deploy_daily_report.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        if result.returncode == 0:
            return {
                "status": "success",
                "message": "Daily report generated and emailed successfully",
                "output": result.stdout,
            }

        # Non‑zero exit code → treat as internal error
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to generate report",
                "error": result.stderr,
            },
        )
    except Exception as exc:
        # Unexpected exception → also return proper 500
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": str(exc)},
        )


