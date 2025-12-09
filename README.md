# US Market Investment Recommendation System

An intelligent investment recommendation system that analyzes news sentiment and provides daily Buy/Hold/Sell recommendations for top US stocks.

## Features

- **Real-time News Analysis**: Fetches latest news from Yahoo Finance for top 20 US stocks
- **Sentiment Analysis**: Analyzes news headlines and summaries using TextBlob
- **Investment Recommendations**: Provides Buy/Hold/Sell recommendations based on sentiment
- **Interactive Dashboard**: Streamlit web interface for real-time data visualization
- **Price Charts**: Interactive charts showing 30-day price history
- **Daily Email Reports**: Automated daily email reports with CSV attachments
- **Cloud Deployment**: Ready for deployment on Railway/Heroku

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
- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **Streamlit Dashboard**: http://localhost:8501

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

### Railway Deployment
1. Fork/clone this repository
2. Connect to Railway
3. Set environment variables in Railway dashboard
4. Deploy automatically

### Environment Variables
- `GMAIL_USER`: Your Gmail address
- `GMAIL_APP_PASSWORD`: Gmail app password
- `RECIPIENT_EMAIL`: Email to receive daily reports

## Stock Coverage

Currently covers top 20 US stocks by market cap:
- AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, BRK-B, UNH, LLY
- JPM, V, XOM, MA, AVGO, PG, HD, COST, MRK, ABBV

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

## Disclaimer

This system is for educational purposes only. Investment decisions should be based on comprehensive research and consultation with financial advisors. Past performance does not guarantee future results. 