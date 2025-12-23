from typing import List, Dict

import datetime as dt

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from textblob import TextBlob

# Use Indian tickers for coverage
from backend.indian_tickers import INDIAN_TICKERS
from backend.newsapi_client import search_news_for_query

# Ticker universe
TICKERS: List[str] = INDIAN_TICKERS


app = FastAPI(title="Indian Market Investment Recommendation API (News-only mode)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _fetch_news_for_ticker(ticker: str) -> List[Dict]:
    """
    Fetch latest news for a single ticker using NewsAPI.ai (or compatible)
    via backend.newsapi_client. Returns empty list on failure.
    """
    try:
        return search_news_for_query(ticker, limit=20)
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
    # Price data is temporarily unavailable until a new provider is configured.
    raise HTTPException(status_code=503, detail="Price data unavailable; provider not configured")


@app.get("/news")
def news():
    """
    Raw news feed for all tickers.
    """
    all_news: List[Dict] = []
    for ticker in TICKERS:
        try:
            all_news.extend(_fetch_news_for_ticker(ticker))
        except Exception:
            # If one ticker fails, continue with others
            continue
    return all_news


@app.get("/sentiment")
def sentiment():
    """
    Per‑article sentiment for all news.
    Analyzes both title and summary together for better sentiment detection.
    """
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
    return results


@app.get("/recommendations")
def recommendations():
    """
    Aggregate sentiment into per‑ticker recommendations.
    Enhanced with MCP technical indicators and fundamentals when available.
    Returns: ticker, avg_polarity, recommendation, confidence, factors.
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
        base_rec = _recommendation_from_score(avg_sentiment)
        
        # Try to enhance with MCP data (may not work for all Indian stocks)
        enhanced = _enhance_recommendation_with_mcp(ticker, avg_sentiment, base_rec)
        
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
    """
    from backend.mcp_integration import get_technical_indicators, get_fundamental_snapshot
    
    factors = {"sentiment": sentiment_score}
    confidence = 0.5  # Base confidence from sentiment only
    
    # Clean ticker for MCP (remove .NS/.BO suffix, MCP might not support Indian stocks)
    clean_ticker = ticker.replace(".NS", "").replace(".BO", "")
    
    # Try to get technical indicators (MCP may only support US stocks)
    try:
        technicals = get_technical_indicators(clean_ticker, period="6mo")
        if technicals and isinstance(technicals, dict) and technicals.get("rsi"):
            factors["technical"] = {
                "rsi": technicals.get("rsi"),
                "sma_20": technicals.get("sma", {}).get("20") if isinstance(technicals.get("sma"), dict) else None,
                "sma_50": technicals.get("sma", {}).get("50") if isinstance(technicals.get("sma"), dict) else None,
            }
            # Adjust recommendation based on RSI
            rsi = technicals.get("rsi", 50)
            if rsi < 30:  # Oversold - bullish
                confidence += 0.1
            elif rsi > 70:  # Overbought - bearish
                confidence -= 0.1
    except Exception as e:
        # MCP might not support this ticker (likely Indian stocks)
        pass
    
    # Try to get fundamentals
    try:
        fundamentals = get_fundamental_snapshot(clean_ticker)
        if fundamentals and isinstance(fundamentals, dict):
            factors["fundamental"] = {
                "pe_ratio": fundamentals.get("trailingPE"),
                "market_cap": fundamentals.get("marketCap"),
            }
            # Adjust confidence based on fundamentals
            pe = fundamentals.get("trailingPE")
            if pe and 0 < pe < 20:  # Reasonable P/E
                confidence += 0.1
    except Exception:
        pass
    
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
        "message": "Indian Market Investment Recommendation API (news/sentiment only; prices temporarily disabled)",
    }


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


