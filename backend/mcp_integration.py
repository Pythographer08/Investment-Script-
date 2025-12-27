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
        
        # yfinance needs .NS/.BO suffix for Indian stocks, so keep it as-is
        # Fetch historical data
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        
        if hist.empty:
            return {}
        
        close_prices = hist["Close"]
        
        # Calculate RSI
        def calculate_rsi(prices: pd.Series, window: int = 14) -> float:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1]) if not rsi.empty else 50.0
        
        rsi_value = calculate_rsi(close_prices, rsi_window)
        
        # Calculate SMAs
        sma_dict = {}
        for window in sma_windows:
            sma = close_prices.rolling(window=window).mean()
            sma_dict[str(window)] = float(sma.iloc[-1]) if not sma.empty else None
        
        # Calculate EMAs
        ema_dict = {}
        for window in ema_windows:
            ema = close_prices.ewm(span=window, adjust=False).mean()
            ema_dict[str(window)] = float(ema.iloc[-1]) if not ema.empty else None
        
        return {
            "rsi": rsi_value,
            "sma": sma_dict,
            "ema": ema_dict,
            "current_price": float(close_prices.iloc[-1]) if not close_prices.empty else None
        }
    except Exception as e:
        # Return empty dict on error (fallback to sentiment-only)
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
        
        # yfinance needs .NS/.BO suffix for Indian stocks, so keep it as-is
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Extract key fundamentals
        fundamentals = {
            "trailingPE": info.get("trailingPE"),
            "forwardPE": info.get("forwardPE"),
            "marketCap": info.get("marketCap"),
            "revenueGrowth": info.get("revenueGrowth"),
            "earningsGrowth": info.get("earningsGrowth"),
            "profitMargins": info.get("profitMargins"),
            "dividendYield": info.get("dividendYield"),
            "currentPrice": info.get("currentPrice"),
            "targetMeanPrice": info.get("targetMeanPrice"),
        }
        
        # Remove None values
        return {k: v for k, v in fundamentals.items() if v is not None}
    except Exception as e:
        # Return empty dict on error (fallback to sentiment-only)
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

