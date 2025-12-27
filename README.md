# US & Indian Market Investment Recommendation System

An intelligent investment recommendation system that analyzes news sentiment and provides daily Buy/Hold/Sell recommendations for top US and Indian stocks.

## Features

- **Real-time News Analysis**: Fetches latest news from Yahoo Finance for 109 stocks (50 US + 59 Indian)
- **Sentiment Analysis**: Analyzes news headlines and summaries using TextBlob
- **Investment Recommendations**: Provides Buy/Hold/Sell recommendations based on sentiment
- **Interactive Dashboard**: Streamlit web interface for real-time data visualization
- **Price Charts**: Interactive charts showing 30-day price history
- **Daily Email Reports**: Automated daily email reports with CSV attachments
- **Cloud Deployment**: Ready for deployment on Render/Streamlit Cloud

## Tech Stack

- **Backend**: FastAPI, Python 3.10
- **Frontend**: Streamlit, Altair
- **Data**: Yahoo Finance API (yfinance)
- **Sentiment Analysis**: TextBlob
- **Email**: SMTP with Gmail
- **Deployment**: Railway/Heroku ready

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
- `GET /news` - Latest news for all tickers
- `GET /sentiment` - Sentiment analysis results
- `GET /recommendations` - Investment recommendations
- `GET /price_chart?ticker=AAPL` - Price chart for specific ticker

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
