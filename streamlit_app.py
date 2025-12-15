import streamlit as st
import requests
import pandas as pd
import altair as alt

API_URL = "https://investment-script.onrender.com"
TICKERS = [
    # Tech / Communication
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "NVDA",
    "META",
    "TSLA",
    "ADBE",
    "NFLX",
    "INTC",
    "CSCO",
    "CRM",
    "AMD",
    "ORCL",
    # Healthcare (10)
    "UNH",
    "LLY",
    "PFE",
    "ABBV",
    "MRK",
    "JNJ",
    "TMO",
    "MDT",
    "BMY",
    "AMGN",
    # Financials (10)
    "JPM",
    "BAC",
    "WFC",
    "C",
    "GS",
    "MS",
    "V",
    "MA",
    "BLK",
    "AXP",
    # Energy / Industrials / Materials (10)
    "XOM",
    "CVX",
    "COP",
    "SLB",
    "EOG",
    "MPC",
    "PSX",
    "KMI",
    "OXY",
    "PXD",
    # Consumer / Retail / Staples (10)
    "WMT",
    "COST",
    "PG",
    "KO",
    "PEP",
    "NKE",
    "MCD",
    "HD",
    "TGT",
    "SBUX",
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
    # News aggregation across many tickers can take a while on Render; give it longer.
    news = requests.get(f"{API_URL}/news", timeout=30).json()
    if news:
        news_df = pd.DataFrame(news)[["ticker", "title", "publisher", "link"]]
        st.dataframe(news_df, use_container_width=True)
    else:
        st.write("No news available.")
except requests.exceptions.Timeout:
    st.error("News request timed out. The backend may be busy; please try again in a few seconds.")
except Exception as e:
    st.error(f"Error loading news: {e}")

# Sentiment Section
st.header("Market Sentiment (Headline + Summary)")
try:
    # Sentiment endpoint is the heaviest (news + TextBlob per article); allow more time.
    sentiment = requests.get(f"{API_URL}/sentiment", timeout=45).json()
    if sentiment:
        sentiment_df = pd.DataFrame(sentiment)[["ticker", "title", "summary", "polarity", "subjectivity"]]
        st.dataframe(sentiment_df, use_container_width=True)
    else:
        st.write("No sentiment data available.")
except requests.exceptions.Timeout:
    st.error("Sentiment request timed out. The backend may still be computing; try again shortly.")
except Exception as e:
    st.error(f"Error loading sentiment: {e}")

# Recommendations Section
st.header("Today's Recommendations")
try:
    # Recommendations depend on sentiment aggregation; use a generous timeout.
    recs = requests.get(f"{API_URL}/recommendations", timeout=45).json()
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
                try:
                    # Delegate email sending to backend so it can use its env vars.
                    resp = requests.get(f"{API_URL}/run-daily-report", timeout=60)
                    if resp.status_code == 200:
                        st.success("✅ Email sent successfully!")
                    else:
                        st.error(f"❌ Error {resp.status_code}: {resp.text}")
                except Exception as e:
                    st.error(f"❌ Failed to send email: {e}")
    else:
        st.write("No recommendations available.")
except requests.exceptions.Timeout:
    st.error("Recommendations request timed out. The backend may still be computing; try again shortly.")
except requests.exceptions.ConnectionError:
    st.error("⚠️ Cannot connect to backend API. Make sure the FastAPI server is running:")
    st.code("uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000")
except Exception as e:
    st.error(f"Error loading recommendations: {e}")
