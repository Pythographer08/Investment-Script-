import streamlit as st
import requests
import pandas as pd
import altair as alt

API_URL = "http://127.0.0.1:8000"
TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "UNH", "LLY",
    "JPM", "V", "XOM", "MA", "AVGO", "PG", "HD", "COST", "MRK", "ABBV"
]

st.title("US Market Investment Recommendations")

# Ticker selection and price chart
st.header("Price Chart")
ticker = st.selectbox("Select a ticker to view its price chart:", TICKERS)
try:
    chart_data = requests.get(f"{API_URL}/price_chart?ticker={ticker}", timeout=10).json()
    if "error" not in chart_data:
        df = pd.DataFrame({"Date": chart_data["dates"], "Close": chart_data["closes"]})
        chart = alt.Chart(df).mark_line().encode(
            x="Date:T",
            y="Close:Q"
        ).properties(title=f"{ticker} - Last 30 Days Closing Prices")
        st.altair_chart(chart, use_container_width=True)
    else:
        st.write("No price data available.")
except requests.exceptions.ConnectionError:
    st.warning("⚠️ Backend API not running. Start it with: `uvicorn backend.main:app --reload`")
except Exception as e:
    st.error(f"Error loading chart: {e}")

# News Section
st.header("Latest News")
try:
    news = requests.get(f"{API_URL}/news", timeout=10).json()
    if news:
        news_df = pd.DataFrame(news)[["ticker", "title", "publisher", "link"]]
        st.dataframe(news_df, use_container_width=True)
    else:
        st.write("No news available.")
except Exception as e:
    st.error(f"Error loading news: {e}")

# Sentiment Section
st.header("Market Sentiment (Headline + Summary)")
try:
    sentiment = requests.get(f"{API_URL}/sentiment", timeout=10).json()
    if sentiment:
        sentiment_df = pd.DataFrame(sentiment)[["ticker", "title", "summary", "polarity", "subjectivity"]]
        st.dataframe(sentiment_df, use_container_width=True)
    else:
        st.write("No sentiment data available.")
except Exception as e:
    st.error(f"Error loading sentiment: {e}")

# Recommendations Section
st.header("Today's Recommendations")
try:
    recs = requests.get(f"{API_URL}/recommendations", timeout=10).json()
    if recs:
        recs_df = pd.DataFrame(recs)[["ticker", "avg_polarity", "recommendation"]]
        st.dataframe(recs_df, use_container_width=True)
        st.markdown("""
        **How to read this:**
        - **Buy**: News sentiment is positive. Consider buying or holding.  
        - **Hold**: News is mixed/neutral. No strong action suggested.  
        - **Sell**: News sentiment is negative. Consider reducing exposure.
        """)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export Recommendations to CSV"):
                recs_df.to_csv("recommendations.csv", index=False)
                st.success("Exported to recommendations.csv")
        with col2:
            if st.button("Send Test Email"):
                import subprocess
                import sys
                try:
                    result = subprocess.run(
                        [sys.executable, "deploy_daily_report.py"],
                        cwd=".",
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    if result.returncode == 0:
                        st.success("✅ Email sent successfully!")
                    else:
                        st.error(f"❌ Error: {result.stderr}")
                except Exception as e:
                    st.error(f"❌ Failed to send email: {e}")
    else:
        st.write("No recommendations available.")
except requests.exceptions.ConnectionError:
    st.error("⚠️ Cannot connect to backend API. Make sure the FastAPI server is running:")
    st.code("uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000")
except Exception as e:
    st.error(f"Error loading recommendations: {e}") 