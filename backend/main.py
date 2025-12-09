from typing import List, Dict

import datetime as dt

import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from textblob import TextBlob

TICKERS: List[str] = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "NVDA",
    "META",
    "TSLA",
    "BRK-B",
    "UNH",
    "LLY",
    "JPM",
    "V",
    "XOM",
    "MA",
    "AVGO",
    "PG",
    "HD",
    "COST",
    "MRK",
    "ABBV",
]


app = FastAPI(title="US Market Investment Recommendation API")

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
                "publisher": provider.get("displayName", ""),
                "link": canonical.get("url", ""),
            }
        )
    return cleaned


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
    Returns: ticker, avg_polarity, recommendation.
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
        avg = sum(scores) / len(scores)
        output.append(
            {
                "ticker": ticker,
                "avg_polarity": avg,
                "recommendation": _recommendation_from_score(avg),
            }
        )

    # Stable ordering like the frontend's list
    ticker_to_row = {row["ticker"]: row for row in output}
    ordered: List[Dict] = []
    for t in TICKERS:
        row = ticker_to_row.get(t)
        if row:
            ordered.append(row)

    # Attach metadata for debugging / logging if needed
    _ = dt.datetime.utcnow()
    return ordered


@app.get("/")
def root():
    return {"status": "ok", "message": "US Market Investment Recommendation API"}


@app.get("/run-daily-report")
def run_daily_report():
    """
    Endpoint to trigger daily report generation (for cloud cron jobs).
    Returns success/error status.
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
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            return {
                "status": "success",
                "message": "Daily report generated and emailed successfully",
                "output": result.stdout
            }
        else:
            return {
                "status": "error",
                "message": "Failed to generate report",
                "error": result.stderr
            }, 500
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }, 500


