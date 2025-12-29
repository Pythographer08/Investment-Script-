"""
MCP (Model Context Protocol) Financial Tools Integration
Integrates MCP financial analysis tools into the recommendation pipeline.
"""
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Note: MCP tools are available via function calls, not direct imports
# This module provides wrapper functions to integrate MCP financial tools


def get_market_snapshot(tickers: List[str]) -> Dict:
    """
    Get real-time market snapshot using MCP financial tools.
    
    Args:
        tickers: List of ticker symbols
        
    Returns:
        Dict with market data for each ticker
    """
    # This will be called via MCP function: mcp_financial-mcp_market_snapshot
    # For now, return placeholder structure
    # TODO: Integrate actual MCP call when backend is ready
    return {}


def get_technical_indicators(
    ticker: str,
    period: str = "6mo",
    sma_windows: List[int] = [20, 50, 200],
    ema_windows: List[int] = [12, 26],
    rsi_window: int = 14
) -> Dict:
    """
    Get technical indicators (RSI, SMA, EMA) for a ticker.
    Uses yfinance as fallback since MCP tools require MCP server connection.
    
    Args:
        ticker: Stock symbol (keep .NS/.BO suffix for Indian stocks)
        period: History period (e.g., "3mo", "6mo", "1y")
        sma_windows: List of SMA periods
        ema_windows: List of EMA periods
        rsi_window: RSI lookback window
        
    Returns:
        Dict with technical indicators: {rsi, sma: {20, 50, 200}, ema: {12, 26}}
    """
    try:
        import yfinance as yf
        import pandas as pd
        import warnings
        
        # yfinance needs .NS/.BO suffix for Indian stocks, so keep it as-is
        # Suppress yfinance warnings about delisted stocks
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            warnings.filterwarnings("ignore", category=FutureWarning)
            
            # Create a fresh Ticker object for each call to avoid caching issues
            stock = yf.Ticker(ticker)
            
            # Fetch historical data with explicit timeout and error handling
            try:
                hist = stock.history(period=period, interval="1d", timeout=10, quiet=True)
            except Exception as e:
                print(f"Error fetching history for {ticker}: {e}")
                return {}
        
        if hist.empty or len(hist) < 20:  # Need at least 20 days for meaningful indicators
            print(f"Warning: Insufficient data for {ticker} (got {len(hist)} rows)")
            return {}
        
        close_prices = hist["Close"]
        
        # Validate we have actual price data
        if close_prices.isna().all() or close_prices.empty:
            print(f"Warning: No valid price data for {ticker}")
            return {}
        
        # Calculate RSI
        def calculate_rsi(prices: pd.Series, window: int = 14) -> float:
            if len(prices) < window + 1:
                return 50.0  # Default neutral RSI
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            # Avoid division by zero
            rs = gain / (loss + 1e-10)
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1]) if not rsi.empty and not pd.isna(rsi.iloc[-1]) else 50.0
        
        rsi_value = calculate_rsi(close_prices, rsi_window)
        
        # Calculate SMAs
        sma_dict = {}
        for window in sma_windows:
            if len(close_prices) >= window:
                sma = close_prices.rolling(window=window).mean()
                sma_val = sma.iloc[-1] if not sma.empty else None
                sma_dict[str(window)] = float(sma_val) if sma_val is not None and not pd.isna(sma_val) else None
            else:
                sma_dict[str(window)] = None
        
        # Calculate EMAs
        ema_dict = {}
        for window in ema_windows:
            if len(close_prices) >= window:
                ema = close_prices.ewm(span=window, adjust=False).mean()
                ema_val = ema.iloc[-1] if not ema.empty else None
                ema_dict[str(window)] = float(ema_val) if ema_val is not None and not pd.isna(ema_val) else None
            else:
                ema_dict[str(window)] = None
        
        current_price = float(close_prices.iloc[-1]) if not close_prices.empty and not pd.isna(close_prices.iloc[-1]) else None
        
        result = {
            "rsi": rsi_value,
            "sma": sma_dict,
            "ema": ema_dict,
            "current_price": current_price
        }
        
        # Debug: Log that we got data for this specific ticker
        print(f"Technical data for {ticker}: RSI={rsi_value:.2f}, Price={current_price}")
        
        return result
    except Exception as e:
        # Log the error for debugging
        print(f"Exception in get_technical_indicators for {ticker}: {e}")
        import traceback
        traceback.print_exc()
        return {}


def get_fundamental_snapshot(ticker: str) -> Dict:
    """
    Get fundamental data (earnings, revenue, valuation) using yfinance.
    Uses yfinance as fallback since MCP tools require MCP server connection.
    
    Args:
        ticker: Stock symbol (keep .NS/.BO suffix for Indian stocks)
        
    Returns:
        Dict with fundamental metrics: {trailingPE, marketCap, revenueGrowth, earningsGrowth, etc.}
    """
    try:
        import yfinance as yf
        import warnings
        
        # yfinance needs .NS/.BO suffix for Indian stocks, so keep it as-is
        # Suppress yfinance warnings about delisted stocks
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            warnings.filterwarnings("ignore", category=FutureWarning)
            
            # Create a fresh Ticker object for each call to avoid caching issues
            stock = yf.Ticker(ticker)
            
            try:
                # Fetch info with explicit timeout
                info = stock.info
                
                # Check if info is empty or invalid
                if not info or len(info) < 5:
                    print(f"Warning: Empty or invalid info for {ticker}")
                    return {}
            except Exception as e:
                print(f"Error fetching info for {ticker}: {e}")
                return {}
        
        # Extract key fundamentals - handle both US and Indian stock formats
        fundamentals = {
            "trailingPE": info.get("trailingPE") or info.get("trailingPegRatio"),
            "forwardPE": info.get("forwardPE") or info.get("forwardPegRatio"),
            "marketCap": info.get("marketCap") or info.get("totalAssets"),
            "revenueGrowth": info.get("revenueGrowth") or info.get("revenuePerShare"),
            "earningsGrowth": info.get("earningsGrowth") or info.get("earningsQuarterlyGrowth"),
            "profitMargins": info.get("profitMargins") or info.get("grossMargins"),
            "dividendYield": info.get("dividendYield") or info.get("dividendRate"),
            "currentPrice": info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose"),
            "targetMeanPrice": info.get("targetMeanPrice") or info.get("targetHighPrice"),
            "bookValue": info.get("bookValue"),
            "priceToBook": info.get("priceToBook"),
        }
        
        # Remove None values and validate data
        cleaned = {k: v for k, v in fundamentals.items() if v is not None}
        
        # Debug: Log that we got data for this specific ticker
        if cleaned:
            print(f"Fundamental data for {ticker}: P/E={cleaned.get('trailingPE')}, MarketCap={cleaned.get('marketCap')}")
        else:
            print(f"Warning: No fundamental data extracted for {ticker}")
        
        return cleaned
    except Exception as e:
        # Log the error for debugging
        print(f"Exception in get_fundamental_snapshot for {ticker}: {e}")
        import traceback
        traceback.print_exc()
        return {}


def enhance_recommendation_with_mcp(
    ticker: str,
    sentiment_score: float,
    base_recommendation: str
) -> Dict:
    """
    Enhance recommendation by combining sentiment with MCP technical/fundamental data.
    
    Args:
        ticker: Stock symbol
        sentiment_score: Sentiment polarity score
        base_recommendation: Base recommendation from sentiment (Buy/Hold/Sell)
        
    Returns:
        Enhanced recommendation dict with:
        - recommendation: Final Buy/Hold/Sell
        - confidence: Confidence score
        - factors: Dict of contributing factors (sentiment, technical, fundamental)
    """
    try:
        # Get technical indicators
        technicals = get_technical_indicators(ticker)
        
        # Get fundamentals
        fundamentals = get_fundamental_snapshot(ticker)
        
        # Combine factors (weighted scoring)
        # TODO: Implement weighted scoring logic
        factors = {
            "sentiment": sentiment_score,
            "technical": technicals,
            "fundamental": fundamentals
        }
        
        # Enhanced recommendation logic
        # For now, return base recommendation
        # TODO: Implement sophisticated scoring
        
        return {
            "ticker": ticker,
            "recommendation": base_recommendation,
            "confidence": 0.5,  # Placeholder
            "factors": factors
        }
    except Exception as e:
        # Fallback to base recommendation if MCP fails
        return {
            "ticker": ticker,
            "recommendation": base_recommendation,
            "confidence": 0.3,
            "factors": {"sentiment": sentiment_score},
            "error": str(e)
        }

