"""
Indian Stock Market API Client
Client for fetching news, prices, and market data from Indian API (indianapi.in).
"""
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

load_dotenv()

# API Configuration for Indian API (stock.indianapi.in)
# Strip whitespace to avoid issues with copied values containing newlines/spaces.
INDIAN_STOCK_API_KEY = (os.getenv("INDIAN_STOCK_API_KEY", "") or "").strip()
INDIAN_STOCK_API_BASE_URL = (os.getenv("INDIAN_STOCK_API_BASE_URL", "https://stock.indianapi.in") or "").strip()
INDIAN_STOCK_API_AUTH_HEADER = (os.getenv("INDIAN_STOCK_API_AUTH_HEADER", "x-api-key") or "x-api-key").strip()  # IndianAPI uses x-api-key


class IndianStockAPI:
    """
    Generic Indian Stock Market API client.
    Configure endpoints and data parsing based on your specific API provider.
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or INDIAN_STOCK_API_KEY
        self.base_url = base_url or INDIAN_STOCK_API_BASE_URL
        self.auth_header = INDIAN_STOCK_API_AUTH_HEADER
        
        if not self.api_key:
            raise ValueError("INDIAN_STOCK_API_KEY must be set in .env or passed as parameter")
        if not self.base_url:
            raise ValueError("INDIAN_STOCK_API_BASE_URL must be set in .env or passed as parameter")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        # Try common authentication patterns
        if self.auth_header.lower() == "authorization":
            return {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        elif self.auth_header.lower() == "x-api-key":
            return {
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        else:
            return {
                self.auth_header: self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
    
    def _get_auth_params(self) -> Dict[str, str]:
        """Get authentication as query parameters (alternative method)."""
        return {"api_key": self.api_key}
    
    def fetch_news(self, ticker: str, limit: int = 10) -> List[Dict]:
        """
        Fetch news for a given Indian stock ticker.
        
        Args:
            ticker: Stock symbol (e.g., "RELIANCE", "TCS", "INFY" or "RELIANCE.NS")
            limit: Maximum number of news items to return
            
        Returns:
            List of news dictionaries with keys: ticker, title, summary, publisher, link
        """
        clean_ticker = ticker.replace(".NS", "").replace(".BO", "")

        # Documented endpoint: /news?stock_name={}
        endpoint = f"{self.base_url}/news"
        params = {"stock_name": clean_ticker, "limit": limit}

        try:
            resp = requests.get(endpoint, headers=self._get_headers(), params=params, timeout=15)
            if resp.status_code == 200:
                return self._parse_news(resp.json(), ticker)
            # Retry with api_key in query if header auth fails
            resp = requests.get(endpoint, params={**self._get_auth_params(), **params}, timeout=15)
            if resp.status_code == 200:
                return self._parse_news(resp.json(), ticker)
            print(f"Warning: news fetch {resp.status_code} body={resp.text[:200]}")
        except requests.exceptions.RequestException as exc:
            print(f"Error fetching news for {ticker}: {exc}")

        return []
    
    def fetch_price_history(self, ticker: str, period_days: int = 30) -> Dict:
        """
        Fetch historical price data for a ticker.
        
        Args:
            ticker: Stock symbol (e.g., "RELIANCE", "TCS" or "RELIANCE.NS")
            period_days: Number of days of history to fetch
            
        Returns:
            Dict with keys: dates (list of strings), closes (list of floats)
        """
        clean_ticker = ticker.replace(".NS", "").replace(".BO", "")

        # Map period_days to API period string
        if period_days <= 30:
            period = "1m"
        elif period_days <= 90:
            period = "3m"
        elif period_days <= 180:
            period = "6m"
        else:
            period = "1y"

        endpoint = f"{self.base_url}/historical_data"
        params = {"stock_name": clean_ticker, "period": period, "filter": "default"}

        try:
            resp = requests.get(endpoint, headers=self._get_headers(), params=params, timeout=15)
            if resp.status_code == 200:
                return self._parse_price_history(resp.json())
            resp = requests.get(endpoint, params={**self._get_auth_params(), **params}, timeout=15)
            if resp.status_code == 200:
                return self._parse_price_history(resp.json())
            print(f"Warning: price history fetch {resp.status_code} body={resp.text[:200]}")
        except requests.exceptions.RequestException as exc:
            print(f"Error fetching price history for {ticker}: {exc}")

        return {"dates": [], "closes": []}
    
    def fetch_current_price(self, ticker: str) -> Dict:
        """
        Fetch current/latest price for a ticker.
        
        Args:
            ticker: Stock symbol (e.g., "RELIANCE", "TCS" or "RELIANCE.NS")
            
        Returns:
            Dict with price information
        """
        clean_ticker = ticker.replace(".NS", "").replace(".BO", "")

        endpoint = f"{self.base_url}/stock"
        params = {"name": clean_ticker}

        try:
            resp = requests.get(endpoint, headers=self._get_headers(), params=params, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            resp = requests.get(endpoint, params={**self._get_auth_params(), **params}, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            print(f"Warning: current price fetch {resp.status_code} body={resp.text[:200]}")
        except requests.exceptions.RequestException as exc:
            print(f"Error fetching current price for {ticker}: {exc}")

        return {}
    
    def _parse_news(self, api_response: Dict, ticker: str) -> List[Dict]:
        """
        Parse API news response into standardized format.
        Handles multiple common response structures.
        """
        # Try different response structures
        news_items = (
            api_response.get("data", []) or
            api_response.get("articles", []) or
            api_response.get("news", []) or
            api_response.get("results", []) or
            (api_response if isinstance(api_response, list) else [])
        )
        
        cleaned = []
        for item in news_items:
            if not isinstance(item, dict):
                continue
                
            cleaned.append({
                "ticker": ticker,
                "title": item.get("title", item.get("headline", "")),
                "summary": item.get("summary", item.get("description", item.get("content", ""))),
                "publisher": (
                    item.get("source", {}).get("name", "") if isinstance(item.get("source"), dict)
                    else item.get("source", item.get("publisher", item.get("author", "")))
                ),
                "link": item.get("url", item.get("link", item.get("webUrl", ""))),
            })
        
        return cleaned
    
    def _parse_price_history(self, api_response: Dict) -> Dict:
        """
        Parse API price history response into standardized format.
        Handles multiple common response structures.
        """
        # Try different response structures
        prices = (
            api_response.get("data", []) or
            api_response.get("prices", []) or
            api_response.get("history", []) or
            api_response.get("candles", []) or
            # IndianAPI historical_data returns {"datasets":[{"values":[[date,price], ...]}]}
            api_response.get("datasets", []) or
            (api_response if isinstance(api_response, list) else [])
        )
        
        dates = []
        closes = []
        
        # Handle dataset structure
        if prices and isinstance(prices, list) and prices and isinstance(prices[0], dict) and prices[0].get("values"):
            values = prices[0].get("values", [])
            for entry in values:
                if isinstance(entry, list) and len(entry) >= 2:
                    date_str, close_price = entry[0], entry[1]
                    try:
                        dates.append(str(date_str))
                        closes.append(float(close_price))
                    except (ValueError, TypeError):
                        continue
            return {"dates": dates, "closes": closes}

        for item in prices:
            if not isinstance(item, dict):
                continue
                
            # Try different date field names
            date_str = (
                item.get("date") or
                item.get("timestamp") or
                item.get("time") or
                item.get("datetime")
            )
            
            # Try different close price field names
            close_price = (
                item.get("close") or
                item.get("closePrice") or
                item.get("c") or
                item.get("price")
            )
            
            if date_str and close_price:
                try:
                    dates.append(str(date_str))
                    closes.append(float(close_price))
                except (ValueError, TypeError):
                    continue
        
        return {"dates": dates, "closes": closes}

