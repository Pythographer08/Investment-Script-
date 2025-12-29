"""
Sector mapping for US and Indian stocks.
Used for sector-based analysis and grouping.
"""

from typing import List

# US Stock Sector Mapping
US_SECTOR_MAP = {
    # Technology
    "AAPL": "Technology",
    "MSFT": "Technology",
    "GOOGL": "Technology",
    "AMZN": "Technology",
    "NVDA": "Technology",
    "META": "Technology",
    "TSLA": "Technology",
    "AVGO": "Technology",
    "ADBE": "Technology",
    "NFLX": "Technology",
    "INTC": "Technology",
    "CSCO": "Technology",
    "CRM": "Technology",
    "AMD": "Technology",
    "ORCL": "Technology",
    
    # Healthcare
    "UNH": "Healthcare",
    "LLY": "Healthcare",
    "PFE": "Healthcare",
    "ABBV": "Healthcare",
    "MRK": "Healthcare",
    "JNJ": "Healthcare",
    "TMO": "Healthcare",
    "MDT": "Healthcare",
    "BMY": "Healthcare",
    "AMGN": "Healthcare",
    
    # Financials
    "JPM": "Financials",
    "BAC": "Financials",
    "WFC": "Financials",
    "C": "Financials",
    "GS": "Financials",
    "MS": "Financials",
    "V": "Financials",
    "MA": "Financials",
    "BLK": "Financials",
    "AXP": "Financials",
    
    # Energy
    "XOM": "Energy",
    "CVX": "Energy",
    "COP": "Energy",
    "SLB": "Energy",
    "EOG": "Energy",
    "MPC": "Energy",
    "PSX": "Energy",
    "KMI": "Energy",
    "OXY": "Energy",
    "VLO": "Energy",
    
    # Consumer
    "WMT": "Consumer",
    "COST": "Consumer",
    "PG": "Consumer",
    "KO": "Consumer",
    "PEP": "Consumer",
}

# Indian Stock Sector Mapping
INDIAN_SECTOR_MAP = {
    # IT / Technology
    "TCS.NS": "IT",
    "INFY.NS": "IT",
    "HCLTECH.NS": "IT",
    "WIPRO.NS": "IT",
    "TECHM.NS": "IT",
    "LTIM.NS": "IT",
    "MINDTREE.NS": "IT",
    "MPHASIS.NS": "IT",
    "COFORGE.NS": "IT",
    "ZENSAR.NS": "IT",
    
    # Banking / Financial Services
    "HDFCBANK.NS": "Banking",
    "ICICIBANK.NS": "Banking",
    "SBIN.NS": "Banking",
    "AXISBANK.NS": "Banking",
    "KOTAKBANK.NS": "Banking",
    "INDUSINDBK.NS": "Banking",
    "BANDHANBNK.NS": "Banking",
    "FEDERALBNK.NS": "Banking",
    "PNB.NS": "Banking",
    "UNIONBANK.NS": "Banking",
    
    # Pharma
    "SUNPHARMA.NS": "Pharma",
    "DRREDDY.NS": "Pharma",
    "CIPLA.NS": "Pharma",
    "LUPIN.NS": "Pharma",
    "TORNTPHARM.NS": "Pharma",
    "GLENMARK.NS": "Pharma",
    "CADILAHC.NS": "Pharma",
    "BIOCON.NS": "Pharma",
    "AUROPHARMA.NS": "Pharma",
    "DIVISLAB.NS": "Pharma",
    
    # FMCG
    "HINDUNILVR.NS": "FMCG",
    "ITC.NS": "FMCG",
    "NESTLEIND.NS": "FMCG",
    "BRITANNIA.NS": "FMCG",
    "DABUR.NS": "FMCG",
    "MARICO.NS": "FMCG",
    "GODREJCP.NS": "FMCG",
    "COLPAL.NS": "FMCG",
    "EMAMILTD.NS": "FMCG",
    "TATACONSUM.NS": "FMCG",
    
    # Energy
    "RELIANCE.NS": "Energy",
    "ONGC.NS": "Energy",
    "IOC.NS": "Energy",
    "BPCL.NS": "Energy",
    "HPCL.NS": "Energy",
    "GAIL.NS": "Energy",
    "ADANIGREEN.NS": "Energy",
    "ADANIPORTS.NS": "Energy",
    "TATAPOWER.NS": "Energy",
    "NTPC.NS": "Energy",
    
    # Auto
    "MARUTI.NS": "Auto",
    "TATAMOTORS.NS": "Auto",
    "M&M.NS": "Auto",
    "BAJAJ-AUTO.NS": "Auto",
    "HEROMOTOCO.NS": "Auto",
    "EICHERMOT.NS": "Auto",
    "ASHOKLEY.NS": "Auto",
    "TVSMOTOR.NS": "Auto",
    "BHARATFORG.NS": "Auto",
    "BOSCHLTD.NS": "Auto",
    
    # Others
    "BHARTIARTL.NS": "Telecom",
    "JSWSTEEL.NS": "Steel",
    "TATASTEEL.NS": "Steel",
}


def get_sector(ticker: str) -> str:
    """
    Get sector for a given ticker.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL", "TCS.NS")
    
    Returns:
        Sector name or "Unknown" if not found
    """
    # Check US stocks first
    if ticker in US_SECTOR_MAP:
        return US_SECTOR_MAP[ticker]
    
    # Check Indian stocks
    if ticker in INDIAN_SECTOR_MAP:
        return INDIAN_SECTOR_MAP[ticker]
    
    return "Unknown"


def get_all_sectors() -> List[str]:
    """Get list of all unique sectors."""
    sectors = set(US_SECTOR_MAP.values()) | set(INDIAN_SECTOR_MAP.values())
    return sorted(list(sectors))

