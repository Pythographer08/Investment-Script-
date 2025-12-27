"""
Top US Stocks (NYSE/NASDAQ) by Market Cap
Covers major sectors: Tech, Healthcare, Financials, Energy, Consumer, etc.
"""

US_TICKERS = [
    # Technology (15)
    "AAPL",   # Apple
    "MSFT",   # Microsoft
    "GOOGL",  # Alphabet (Google)
    "AMZN",   # Amazon
    "NVDA",   # NVIDIA
    "META",   # Meta (Facebook)
    "TSLA",   # Tesla
    "AVGO",   # Broadcom
    "ADBE",   # Adobe
    "NFLX",   # Netflix
    "INTC",   # Intel
    "CSCO",   # Cisco
    "CRM",    # Salesforce
    "AMD",    # Advanced Micro Devices
    "ORCL",   # Oracle
    
    # Healthcare (10)
    "UNH",    # UnitedHealth
    "LLY",    # Eli Lilly
    "PFE",    # Pfizer
    "ABBV",   # AbbVie
    "MRK",    # Merck
    "JNJ",    # Johnson & Johnson
    "TMO",    # Thermo Fisher Scientific
    "MDT",    # Medtronic
    "BMY",    # Bristol-Myers Squibb
    "AMGN",   # Amgen
    
    # Financials (10)
    "JPM",    # JPMorgan Chase
    "BAC",    # Bank of America
    "WFC",    # Wells Fargo
    "C",      # Citigroup
    "GS",     # Goldman Sachs
    "MS",     # Morgan Stanley
    "V",      # Visa
    "MA",     # Mastercard
    "BLK",    # BlackRock
    "AXP",    # American Express
    
    # Energy (10)
    "XOM",    # Exxon Mobil
    "CVX",    # Chevron
    "COP",    # ConocoPhillips
    "SLB",    # Schlumberger
    "EOG",    # EOG Resources
    "MPC",    # Marathon Petroleum
    "PSX",    # Phillips 66
    "KMI",    # Kinder Morgan
    "OXY",    # Occidental Petroleum
    "VLO",    # Valero Energy
    
    # Consumer (5)
    "WMT",    # Walmart
    "COST",   # Costco
    "PG",     # Procter & Gamble
    "KO",     # Coca-Cola
    "PEP",    # PepsiCo
]

# Validation: Ensure no duplicates
_duplicates = [ticker for ticker in US_TICKERS if US_TICKERS.count(ticker) > 1]
if _duplicates:
    raise ValueError(f"Duplicate tickers found in US_TICKERS: {set(_duplicates)}")

