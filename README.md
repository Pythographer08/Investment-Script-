# US & Indian Market Investment Recommendation System

An intelligent investment recommendation system that analyzes news sentiment and provides daily Buy/Hold/Sell recommendations for top US and Indian stocks.

## Features

- **Real-time News Analysis**: Fetches latest news from Yahoo Finance for 109 stocks (50 US + 59 Indian)
- **Sentiment Analysis**: Analyzes news headlines and summaries using TextBlob
- **Investment Recommendations**: Provides Buy/Hold/Sell recommendations based on sentiment with news_count
- **Technical Analysis**: On-demand RSI, SMA, and EMA indicators for individual stocks
- **Fundamental Analysis**: On-demand P/E ratios, market cap, growth metrics, and dividend yield
- **Interactive Dashboard**: Streamlit web interface with tabbed navigation for easy data exploration
- **Price Charts**: Interactive charts showing 30-day price history with optional technical/fundamental analysis
- **Smart Caching**: 5-minute cache for news and sentiment to reduce API calls and improve performance
- **Daily Email Reports**: Automated daily email reports with CSV attachments
- **Cloud Deployment**: Ready for deployment on Render/Streamlit Cloud

## Tech Stack

- **Backend**: FastAPI, Python 3.10
- **Frontend**: Streamlit, Altair
- **Data**: Yahoo Finance API (yfinance)
- **Sentiment Analysis**: TextBlob
- **Technical Analysis**: RSI, SMA, EMA calculations
- **Caching**: In-memory cache with 5-minute TTL
- **Email**: SMTP with Gmail
- **Deployment**: Render (Backend), Streamlit Cloud (Frontend)

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd investment-recommendation-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Gmail credentials
   ```

4. **Run the application**
   ```bash
   # Start backend
   uvicorn backend.main:app --reload
   
   # Start dashboard (in another terminal)
   streamlit run streamlit_app.py
   ```

## Usage

### Local Development

**Note:** The links below only work when the services are running. Follow the steps below to start them.

1. **Start the Backend API** (Terminal 1):
   ```bash
   cd C:\Users\niki3\.streamlit
   uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
   ```
   Once running, access:
   - **Backend API**: http://127.0.0.1:8000
   - **API Documentation**: http://127.0.0.1:8000/docs

2. **Start the Streamlit Dashboard** (Terminal 2):
   ```bash
   cd C:\Users\niki3\.streamlit
   streamlit run streamlit_app.py
   ```
   Once running, access:
   - **Streamlit Dashboard**: http://localhost:8501

**Important:** Keep both terminals open while using the app. The Streamlit dashboard requires the backend API to be running.

### API Endpoints

**Core Endpoints:**
- `GET /news` - Latest news for all tickers (cached 5 minutes)
- `GET /sentiment` - Sentiment analysis results (cached 5 minutes)
- `GET /recommendations` - Investment recommendations with news_count
- `GET /price_chart?ticker=AAPL` - Price chart for specific ticker

**Analysis Endpoints (On-Demand):**
- `GET /technical/{ticker}` - Technical indicators (RSI, SMA, EMA) for a specific ticker
- `GET /fundamental/{ticker}` - Fundamental data (P/E, market cap, growth) for a specific ticker
- `GET /analysis/{ticker}` - Combined technical and fundamental analysis for a specific ticker

**Utility Endpoints:**
- `GET /health` - Health check endpoint for deployment monitoring
- `GET /run-daily-report` - Trigger daily email report generation

### Using Analysis Endpoints

The analysis endpoints allow you to fetch technical and fundamental data for specific stocks on-demand:

```bash
# Get technical indicators for Apple
curl https://your-api.onrender.com/technical/AAPL

# Get fundamentals for TCS
curl https://your-api.onrender.com/technical/TCS.NS

# Get combined analysis for Microsoft
curl https://your-api.onrender.com/analysis/MSFT
```

**Technical Indicators Include:**
- RSI (Relative Strength Index) - Identifies overbought/oversold conditions
- SMA (Simple Moving Averages) - 20, 50, and 200-day averages
- EMA (Exponential Moving Averages) - 12 and 26-day averages
- Current price

**Fundamental Metrics Include:**
- P/E Ratios (Trailing and Forward)
- Market Capitalization
- Revenue and Earnings Growth
- Profit Margins
- Dividend Yield
- Analyst Target Price

### Daily Reports
Run manually:
```bash
python deploy_daily_report.py
```

## Deployment

### Render Deployment (Backend)
1. Fork/clone this repository
2. Connect to Render
3. Set environment variables in Render dashboard
4. Deploy automatically

### Streamlit Cloud Deployment (Frontend)
1. Connect your GitHub repository to Streamlit Cloud
2. Set `API_URL` environment variable to your Render backend URL
3. Deploy automatically

### Environment Variables
- `GMAIL_USER`: Your Gmail address
- `GMAIL_APP_PASSWORD`: Gmail app password
- `RECIPIENT_EMAIL`: Email to receive daily reports

## Stock Coverage

Currently covers **109 stocks** across US and Indian markets:

**US Stocks (50)**: Technology (AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, etc.), Healthcare (UNH, LLY, PFE, ABBV, etc.), Financials (JPM, BAC, V, MA, etc.), Energy (XOM, CVX, COP, etc.), Consumer (WMT, COST, PG, KO, etc.)

**Indian Stocks (59)**: IT (TCS, INFY, HCLTECH, WIPRO, etc.), Banking (HDFCBANK, ICICIBANK, SBIN, etc.), Pharma (SUNPHARMA, DRREDDY, CIPLA, etc.), FMCG (HINDUNILVR, ITC, NESTLEIND, etc.), Energy (RELIANCE, ONGC, etc.), Auto (MARUTI, TATAMOTORS, etc.), and more

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

## Disclaimer

This system is for educational purposes only. Investment decisions should be based on comprehensive research and consultation with financial advisors. Past performance does not guarantee future results. 
