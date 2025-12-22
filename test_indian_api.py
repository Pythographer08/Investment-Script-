"""
Test script to discover Indian API endpoints and response formats.
Run this to test the API connection and see what endpoints work.
"""
import os
from dotenv import load_dotenv
from backend.indian_stock_api import IndianStockAPI

load_dotenv()

def test_api():
    """Test the Indian API with a sample ticker."""
    try:
        api = IndianStockAPI()
        print(f"[OK] API client initialized")
        print(f"   Base URL: {api.base_url}")
        print(f"   Auth Header: {api.auth_header}")
        print()
        
        # Test with a common Indian stock
        test_ticker = "RELIANCE"  # Reliance Industries
        
        print(f"Testing news endpoint for {test_ticker}...")
        news = api.fetch_news(test_ticker, limit=5)
        print(f"   Found {len(news)} news items")
        if news:
            print(f"   Sample: {news[0]}")
        print()
        
        print(f"Testing price history for {test_ticker}...")
        prices = api.fetch_price_history(test_ticker, period_days=30)
        print(f"   Found {len(prices.get('dates', []))} price points")
        if prices.get('dates'):
            print(f"   Date range: {prices['dates'][0]} to {prices['dates'][-1]}")
        print()
        
        print(f"Testing current price for {test_ticker}...")
        quote = api.fetch_current_price(test_ticker)
        print(f"   Response: {quote}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api()

