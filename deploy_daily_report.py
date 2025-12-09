import csv
import os
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import List, Dict

import smtplib

from dotenv import load_dotenv

from backend.main import TICKERS, _fetch_news_for_ticker, _analyze_sentiment, _recommendation_from_score


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_CSV = BASE_DIR / "recommendations_daily.csv"


def generate_recommendations() -> List[Dict]:
    """
    Standalone generation of recommendations so this script does NOT
    require the FastAPI server to be running.
    """
    all_news: List[Dict] = []
    for t in TICKERS:
        try:
            fetched = _fetch_news_for_ticker(t)
            all_news.extend(fetched)
            if t == TICKERS[0] and fetched:  # Debug: show first ticker's first item
                sample = fetched[0] if fetched else None
                if sample:
                    print(f"Sample cleaned news item for {t}: title='{sample.get('title', '')[:50]}...'")
        except Exception as e:
            print(f"Warning: Failed to fetch news for {t}: {e}")
            import traceback
            traceback.print_exc()
            continue

    print(f"Fetched {len(all_news)} total news items across all tickers")
    
    if not all_news:
        print("Warning: No news items fetched for any ticker!")
        return []

    # Per‑article sentiment
    per_article: List[Dict] = []
    empty_count = 0
    for item in all_news:
        title = item.get("title", "")
        summary = item.get("summary", "")
        # Combine title + summary for richer sentiment analysis
        combined_text = f"{title} {summary}".strip()
        if not combined_text:
            # Skip empty items
            empty_count += 1
            continue
        scores = _analyze_sentiment(combined_text)
        per_article.append(
            {
                "ticker": item.get("ticker"),
                "polarity": scores["polarity"],
            }
        )
    
    print(f"Analyzed {len(per_article)} articles with text (skipped {empty_count} empty items)")

    # Aggregate
    by_ticker: Dict[str, List[float]] = {}
    for row in per_article:
        t = row["ticker"]
        if t is None:
            continue
        by_ticker.setdefault(t, []).append(float(row["polarity"]))

    rows: List[Dict] = []
    for ticker in TICKERS:
        scores = by_ticker.get(ticker, [])
        if not scores:
            continue
        avg = sum(scores) / len(scores)
        rows.append(
            {
                "ticker": ticker,
                "avg_polarity": round(avg, 3),
                "recommendation": _recommendation_from_score(avg),
                "news_count": len(scores),
            }
        )
    
    print(f"Generated {len(rows)} recommendations")
    if rows:
        print(f"Sample: {rows[0]}")
    
    return rows


def write_csv(rows: List[Dict]) -> Path:
    """
    Write recommendations to CSV.
    """
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["ticker", "avg_polarity", "recommendation", "news_count"]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return OUTPUT_CSV


def send_email_with_attachment(csv_path: Path) -> None:
    """
    Send the CSV as an email attachment using Gmail SMTP.
    Requires env vars:
      - GMAIL_USER
      - GMAIL_APP_PASSWORD
      - RECIPIENT_EMAIL
    """
    load_dotenv()

    gmail_user = os.getenv("GMAIL_USER")
    # Strip spaces which often appear when copying 16‑char Gmail app passwords
    raw_pass = os.getenv("GMAIL_APP_PASSWORD") or ""
    gmail_pass = raw_pass.replace(" ", "")
    recipient = os.getenv("RECIPIENT_EMAIL")

    if not gmail_user or not gmail_pass or not recipient:
        raise RuntimeError("GMAIL_USER, GMAIL_APP_PASSWORD, and RECIPIENT_EMAIL must be set")
    
    # Debug: show what we're using (mask password)
    print(f"Attempting to send email from: {gmail_user}")
    print(f"Password length: {len(gmail_pass)} characters")
    print(f"Sending to: {recipient}")

    msg = EmailMessage()
    msg["Subject"] = f"Daily Investment Recommendations - {datetime.utcnow().strftime('%Y-%m-%d')}"
    msg["From"] = gmail_user
    msg["To"] = recipient

    msg.set_content(
        "Attached is today's US market investment recommendations CSV.\n\n"
        "This file was generated automatically by the investment recommendation system."
    )

    with csv_path.open("rb") as f:
        data = f.read()
    msg.add_attachment(
        data,
        maintype="text",
        subtype="csv",
        filename=csv_path.name,
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(gmail_user, gmail_pass)
        smtp.send_message(msg)


def main() -> None:
    rows = generate_recommendations()
    if not rows:
        raise RuntimeError("No recommendations generated; aborting email send.")
    csv_path = write_csv(rows)
    send_email_with_attachment(csv_path)


if __name__ == "__main__":
    main()


