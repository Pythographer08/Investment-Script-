import streamlit as st
import requests
import pandas as pd
import altair as alt

# Import combined US and Indian tickers
from backend.us_tickers import US_TICKERS
from backend.indian_tickers import INDIAN_TICKERS

API_URL = "https://investment-script.onrender.com"
TICKERS = US_TICKERS + INDIAN_TICKERS

# Page config
st.set_page_config(page_title="Investment Recommendations", layout="wide")

st.title("📈 US & Indian Market Investment Recommendations")

# Helper function to determine market
def get_market(ticker: str) -> str:
    return "Indian" if ticker.endswith((".NS", ".BO")) else "US"

# Helper function for color coding
def get_recommendation_color(recommendation: str) -> str:
    colors = {"Buy": "🟢", "Hold": "🟡", "Sell": "🔴"}
    return colors.get(recommendation, "⚪")

# Sidebar for filters and navigation
st.sidebar.header("🔍 Filters & Navigation")

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📰 News", "💹 Price Charts", "📧 Reports"])

# ========== TAB 1: DASHBOARD ==========
with tab1:
    # Summary metrics section
    st.subheader("📊 Market Overview")
    
    try:
        with st.spinner("Loading recommendations..."):
            try:
                recs = requests.get(f"{API_URL}/recommendations", timeout=120).json()
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. The backend is fetching news for 109 stocks - this may take up to 2 minutes on first load. Please try again in a moment.")
                st.stop()
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Error connecting to backend: {e}")
                st.stop()
        
        if recs:
            recs_df = pd.DataFrame(recs)
            
            # Add market column
            recs_df["market"] = recs_df["ticker"].apply(get_market)
            
            # Summary metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            
            total_stocks = len(recs_df)
            buy_count = len(recs_df[recs_df["recommendation"] == "Buy"])
            hold_count = len(recs_df[recs_df["recommendation"] == "Hold"])
            sell_count = len(recs_df[recs_df["recommendation"] == "Sell"])
            avg_sentiment = recs_df["avg_polarity"].mean()
            
            with col1:
                st.metric("Total Stocks", total_stocks)
            with col2:
                st.metric("🟢 Buy", buy_count, delta=f"{buy_count/total_stocks*100:.1f}%")
            with col3:
                st.metric("🟡 Hold", hold_count, delta=f"{hold_count/total_stocks*100:.1f}%")
            with col4:
                st.metric("🔴 Sell", sell_count, delta=f"{sell_count/total_stocks*100:.1f}%")
            with col5:
                sentiment_color = "normal" if avg_sentiment > 0 else "inverse"
                st.metric("Avg Sentiment", f"{avg_sentiment:.3f}", delta=None)
            
            st.divider()
            
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                market_filter = st.multiselect("Filter by Market", ["US", "Indian"], default=["US", "Indian"])
            with col2:
                rec_filter = st.multiselect("Filter by Recommendation", ["Buy", "Hold", "Sell"], default=["Buy", "Hold", "Sell"])
            with col3:
                search_ticker = st.text_input("🔍 Search Ticker", placeholder="e.g., AAPL, TCS.NS")
            
            # Apply filters
            filtered_df = recs_df.copy()
            if market_filter:
                filtered_df = filtered_df[filtered_df["market"].isin(market_filter)]
            if rec_filter:
                filtered_df = filtered_df[filtered_df["recommendation"].isin(rec_filter)]
            if search_ticker:
                filtered_df = filtered_df[filtered_df["ticker"].str.contains(search_ticker.upper(), case=False)]
            
            # Sort options
            sort_by = st.selectbox("Sort by", ["Sentiment (High to Low)", "Sentiment (Low to High)", "Ticker (A-Z)", "Ticker (Z-A)"])
            if sort_by == "Sentiment (High to Low)":
                filtered_df = filtered_df.sort_values("avg_polarity", ascending=False)
            elif sort_by == "Sentiment (Low to High)":
                filtered_df = filtered_df.sort_values("avg_polarity", ascending=True)
            elif sort_by == "Ticker (A-Z)":
                filtered_df = filtered_df.sort_values("ticker", ascending=True)
            else:
                filtered_df = filtered_df.sort_values("ticker", ascending=False)
            
            st.divider()
            
            # Display recommendations with color coding
            st.subheader(f"📋 Recommendations ({len(filtered_df)} stocks)")
            
            # Format dataframe with colors (handle missing news_count column)
            display_cols = ["ticker", "market", "avg_polarity", "recommendation"]
            if "news_count" in filtered_df.columns:
                display_cols.append("news_count")
            
            display_df = filtered_df[display_cols].copy()
            display_df["recommendation"] = display_df["recommendation"].apply(
                lambda x: f"{get_recommendation_color(x)} {x}"
            )
            display_df["avg_polarity"] = display_df["avg_polarity"].apply(lambda x: f"{x:.3f}")
            
            column_names = ["Ticker", "Market", "Sentiment", "Recommendation"]
            if "news_count" in display_df.columns:
                column_names.append("News Count")
            display_df.columns = column_names
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Market comparison chart
            st.subheader("📊 Market Comparison")
            market_summary = recs_df.groupby("market")["recommendation"].value_counts().unstack(fill_value=0)
            market_summary = market_summary.reindex(columns=["Buy", "Hold", "Sell"], fill_value=0)
            
            chart_data = market_summary.reset_index().melt(id_vars="market", var_name="Recommendation", value_name="Count")
            chart = alt.Chart(chart_data).mark_bar().encode(
                x="market:N",
                y="Count:Q",
                color=alt.Color("Recommendation:N", scale=alt.Scale(domain=["Buy", "Hold", "Sell"], range=["#00ff00", "#ffff00", "#ff0000"])),
                column="Recommendation:N"
            ).properties(width=150, height=200)
            st.altair_chart(chart)
            
            # Export and email buttons
            col1, col2 = st.columns(2)
            with col1:
                export_cols = ["ticker", "market", "avg_polarity", "recommendation"]
                if "news_count" in filtered_df.columns:
                    export_cols.append("news_count")
                csv = filtered_df[export_cols].to_csv(index=False)
                st.download_button(
                    "📥 Export to CSV",
                    csv,
                    "recommendations.csv",
                    "text/csv",
                    key="download-csv"
                )
            with col2:
                if st.button("📧 Send Test Email"):
                    try:
                        with st.spinner("Sending email..."):
                            resp = requests.get(f"{API_URL}/run-daily-report", timeout=60)
                        if resp.status_code == 200:
                            st.success("✅ Email sent successfully!")
                        else:
                            st.error(f"❌ Error {resp.status_code}: {resp.text}")
                    except Exception as e:
                        st.error(f"❌ Failed to send email: {e}")
            
            st.markdown("""
            **💡 How to read recommendations:**
            - **🟢 Buy**: News sentiment is positive. Consider buying or holding.
            - **🟡 Hold**: News is mixed/neutral. No strong action suggested.
            - **🔴 Sell**: News sentiment is negative. Consider reducing exposure.
            """)
        else:
            st.warning("No recommendations available.")
    except requests.exceptions.Timeout:
        st.error("⏱️ Recommendations request timed out. The backend may still be computing; try again shortly.")
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to backend API. Make sure the FastAPI server is running.")
    except Exception as e:
        st.error(f"❌ Error loading recommendations: {e}")

# ========== TAB 2: NEWS ==========
with tab2:
    st.subheader("📰 Latest Market News")
    
    # News filters
    col1, col2 = st.columns(2)
    with col1:
        news_market_filter = st.multiselect("Filter News by Market", ["US", "Indian"], default=["US", "Indian"], key="news_market")
    with col2:
        news_ticker_search = st.text_input("🔍 Search News by Ticker", placeholder="e.g., AAPL, TCS.NS", key="news_ticker")
    
    try:
        with st.spinner("Loading news..."):
            try:
                news = requests.get(f"{API_URL}/news", timeout=120).json()
            except requests.exceptions.Timeout:
                st.error("⏱️ News request timed out. Please try again in a moment.")
                st.stop()
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Error loading news: {e}")
                st.stop()
        
        if news:
            news_df = pd.DataFrame(news)
            news_df["market"] = news_df["ticker"].apply(get_market)
            
            # Apply filters
            if news_market_filter:
                news_df = news_df[news_df["market"].isin(news_market_filter)]
            if news_ticker_search:
                news_df = news_df[news_df["ticker"].str.contains(news_ticker_search.upper(), case=False)]
            
            st.write(f"**Found {len(news_df)} articles**")
            
            # Display news with clickable links
            for idx, row in news_df.iterrows():
                with st.expander(f"📰 {row['ticker']} - {row['title'][:80]}..."):
                    st.write(f"**Publisher:** {row.get('publisher', 'Unknown')}")
                    st.write(f"**Summary:** {row.get('summary', 'No summary available')}")
                    if row.get('link'):
                        st.markdown(f"[🔗 Read full article]({row['link']})")
        else:
            st.info("No news available at the moment.")
    except requests.exceptions.Timeout:
        st.error("⏱️ News request timed out. The backend may be busy; please try again in a few seconds.")
    except Exception as e:
        st.error(f"❌ Error loading news: {e}")

# ========== TAB 3: PRICE CHARTS ==========
with tab3:
    st.subheader("💹 Stock Price Charts & Analysis")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        chart_ticker = st.selectbox("Select a ticker to view its price chart:", TICKERS, key="chart_ticker")
    with col2:
        period_options = ["1mo", "3mo", "6mo", "1y"]
        # Note: Backend currently only supports 1mo, but UI is ready for expansion
        st.write("**Period:** 1 month (30 days)")
    
    # Toggle for technical/fundamental analysis
    show_analysis = st.checkbox("📊 Show Technical & Fundamental Analysis", value=False, key="show_analysis")
    
    try:
        with st.spinner("Loading price data..."):
            chart_data = requests.get(f"{API_URL}/price_chart?ticker={chart_ticker}", timeout=10).json()
        
        if "error" not in chart_data and chart_data.get("dates"):
            df = pd.DataFrame({"Date": chart_data["dates"], "Close": chart_data["closes"]})
            df["Date"] = pd.to_datetime(df["Date"])
            
            # Price metrics
            current_price = df["Close"].iloc[-1]
            price_change = df["Close"].iloc[-1] - df["Close"].iloc[0]
            price_change_pct = (price_change / df["Close"].iloc[0]) * 100
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Price", f"${current_price:.2f}")
            with col2:
                st.metric("30-Day Change", f"${price_change:.2f}", f"{price_change_pct:.2f}%")
            with col3:
                st.metric("Market", get_market(chart_ticker))
            
            # Enhanced chart with area
            chart = alt.Chart(df).mark_area(
                line={'color': '#1f77b4'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='white', offset=0),
                           alt.GradientStop(color='#1f77b4', offset=1)],
                    x1=1, x2=1, y1=1, y2=0
                )
            ).encode(
                x=alt.X("Date:T", title="Date"),
                y=alt.Y("Close:Q", title="Closing Price ($)", scale=alt.Scale(zero=False))
            ).properties(
                title=f"{chart_ticker} - Last 30 Days Closing Prices",
                width=700,
                height=400
            )
            st.altair_chart(chart, use_container_width=True)
            
            # Technical & Fundamental Analysis Section
            if show_analysis:
                st.divider()
                st.subheader("📊 Technical & Fundamental Analysis")
                
                # Fetch analysis data
                try:
                    with st.spinner("Loading analysis data..."):
                        analysis_data = requests.get(f"{API_URL}/analysis/{chart_ticker}", timeout=15).json()
                    
                    # Technical Indicators
                    if analysis_data.get("technical"):
                        st.markdown("### 📈 Technical Indicators")
                        tech = analysis_data["technical"]
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            rsi = tech.get("rsi", 0)
                            rsi_color = "normal" if 30 <= rsi <= 70 else "inverse"
                            rsi_label = "RSI"
                            if rsi < 30:
                                rsi_label += " (Oversold)"
                            elif rsi > 70:
                                rsi_label += " (Overbought)"
                            st.metric(rsi_label, f"{rsi:.2f}", delta=None)
                        
                        with col2:
                            sma_20 = tech.get("sma", {}).get("20")
                            if sma_20:
                                st.metric("SMA 20", f"${sma_20:.2f}")
                            else:
                                st.metric("SMA 20", "N/A")
                        
                        with col3:
                            sma_50 = tech.get("sma", {}).get("50")
                            if sma_50:
                                st.metric("SMA 50", f"${sma_50:.2f}")
                            else:
                                st.metric("SMA 50", "N/A")
                        
                        with col4:
                            current = tech.get("current_price")
                            if current:
                                st.metric("Current Price", f"${current:.2f}")
                            else:
                                st.metric("Current Price", "N/A")
                        
                        # RSI interpretation
                        if rsi < 30:
                            st.info("🟢 **RSI indicates oversold conditions** - Potential buying opportunity")
                        elif rsi > 70:
                            st.warning("🔴 **RSI indicates overbought conditions** - Consider taking profits")
                        else:
                            st.success("🟡 **RSI in neutral range** - No extreme conditions")
                    
                    # Fundamental Data
                    if analysis_data.get("fundamental"):
                        st.markdown("### 💼 Fundamental Metrics")
                        fund = analysis_data["fundamental"]
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            pe = fund.get("trailingPE")
                            if pe:
                                st.metric("Trailing P/E", f"{pe:.2f}")
                            else:
                                st.metric("Trailing P/E", "N/A")
                        
                        with col2:
                            forward_pe = fund.get("forwardPE")
                            if forward_pe:
                                st.metric("Forward P/E", f"{forward_pe:.2f}")
                            else:
                                st.metric("Forward P/E", "N/A")
                        
                        with col3:
                            market_cap = fund.get("marketCap")
                            if market_cap:
                                # Format market cap
                                if market_cap >= 1e12:
                                    cap_str = f"${market_cap/1e12:.2f}T"
                                elif market_cap >= 1e9:
                                    cap_str = f"${market_cap/1e9:.2f}B"
                                elif market_cap >= 1e6:
                                    cap_str = f"${market_cap/1e6:.2f}M"
                                else:
                                    cap_str = f"${market_cap:.2f}"
                                st.metric("Market Cap", cap_str)
                            else:
                                st.metric("Market Cap", "N/A")
                        
                        with col4:
                            div_yield = fund.get("dividendYield")
                            if div_yield:
                                st.metric("Dividend Yield", f"{div_yield*100:.2f}%")
                            else:
                                st.metric("Dividend Yield", "N/A")
                        
                        # Growth metrics
                        col1, col2 = st.columns(2)
                        with col1:
                            rev_growth = fund.get("revenueGrowth")
                            if rev_growth is not None:
                                growth_color = "normal" if rev_growth > 0 else "inverse"
                                st.metric("Revenue Growth", f"{rev_growth*100:.2f}%", delta=None)
                            else:
                                st.metric("Revenue Growth", "N/A")
                        
                        with col2:
                            earn_growth = fund.get("earningsGrowth")
                            if earn_growth is not None:
                                growth_color = "normal" if earn_growth > 0 else "inverse"
                                st.metric("Earnings Growth", f"{earn_growth*100:.2f}%", delta=None)
                            else:
                                st.metric("Earnings Growth", "N/A")
                        
                        # Target price
                        target = fund.get("targetMeanPrice")
                        if target and current_price:
                            target_change = ((target - current_price) / current_price) * 100
                            st.metric("Analyst Target Price", f"${target:.2f}", f"{target_change:+.2f}%")
                
                except requests.exceptions.Timeout:
                    st.warning("⏱️ Analysis request timed out. This may take a moment for some stocks.")
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 404:
                        st.info("ℹ️ Analysis data not available for this ticker. This is normal for some stocks.")
                    else:
                        st.error(f"❌ Error loading analysis: {e}")
                except Exception as e:
                    st.warning(f"⚠️ Could not load analysis data: {str(e)}")
        else:
            st.warning("No price data available for this ticker.")
    except requests.exceptions.ConnectionError:
        st.warning("⚠️ Backend API not running. Start it with: `uvicorn backend.main:app --reload`")
    except Exception as e:
        st.error(f"❌ Error loading chart: {e}")

# ========== TAB 4: SENTIMENT ANALYSIS ==========
with tab4:
    st.subheader("📊 Detailed Sentiment Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        sentiment_market_filter = st.multiselect("Filter by Market", ["US", "Indian"], default=["US", "Indian"], key="sentiment_market")
    with col2:
        sentiment_ticker_search = st.text_input("🔍 Search by Ticker", placeholder="e.g., AAPL, TCS.NS", key="sentiment_ticker")
    
    try:
        with st.spinner("Loading sentiment data (this may take a moment)..."):
            try:
                sentiment = requests.get(f"{API_URL}/sentiment", timeout=120).json()
            except requests.exceptions.Timeout:
                st.error("⏱️ Sentiment request timed out. Please try again in a moment.")
                st.stop()
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Error loading sentiment: {e}")
                st.stop()
        
        if sentiment:
            sentiment_df = pd.DataFrame(sentiment)
            sentiment_df["market"] = sentiment_df["ticker"].apply(get_market)
            
            # Apply filters
            if sentiment_market_filter:
                sentiment_df = sentiment_df[sentiment_df["market"].isin(sentiment_market_filter)]
            if sentiment_ticker_search:
                sentiment_df = sentiment_df[sentiment_df["ticker"].str.contains(sentiment_ticker_search.upper(), case=False)]
            
            st.write(f"**Found {len(sentiment_df)} sentiment analyses**")
            
            # Sentiment distribution chart
            st.subheader("Sentiment Distribution")
            sentiment_bins = pd.cut(sentiment_df["polarity"], bins=[-1, -0.1, 0.1, 1], labels=["Negative", "Neutral", "Positive"])
            sentiment_dist = sentiment_bins.value_counts()
            
            dist_chart = alt.Chart(pd.DataFrame({
                "Sentiment": sentiment_dist.index,
                "Count": sentiment_dist.values
            })).mark_bar().encode(
                x="Sentiment:N",
                y="Count:Q",
                color=alt.Color("Sentiment:N", scale=alt.Scale(
                    domain=["Negative", "Neutral", "Positive"],
                    range=["#ff4444", "#ffaa00", "#44ff44"]
                ))
            ).properties(width=600, height=300)
            st.altair_chart(dist_chart, use_container_width=True)
            
            # Display sentiment data
            display_sentiment_df = sentiment_df[["ticker", "market", "title", "polarity", "subjectivity"]].copy()
            display_sentiment_df["polarity"] = display_sentiment_df["polarity"].apply(lambda x: f"{x:.3f}")
            display_sentiment_df["subjectivity"] = display_sentiment_df["subjectivity"].apply(lambda x: f"{x:.3f}")
            display_sentiment_df.columns = ["Ticker", "Market", "Title", "Polarity", "Subjectivity"]
            
            st.dataframe(display_sentiment_df, use_container_width=True, hide_index=True)
        else:
            st.info("No sentiment data available.")
    except requests.exceptions.Timeout:
        st.error("⏱️ Sentiment request timed out. The backend may still be computing; try again shortly.")
    except Exception as e:
        st.error(f"❌ Error loading sentiment: {e}")
