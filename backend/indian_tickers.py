"""
Top Indian Stocks (NSE/BSE) by Market Cap
Covers major sectors: IT, Banking, Pharma, FMCG, Auto, Energy, etc.
"""

# NSE ticker format: SYMBOL.NS (e.g., RELIANCE.NS)
# BSE ticker format: SYMBOL.BO (e.g., RELIANCE.BO)
# Using NSE format by default (.NS suffix)

INDIAN_TICKERS = [
    # IT / Technology (10)
    "TCS.NS",      # Tata Consultancy Services
    "INFY.NS",     # Infosys
    "HCLTECH.NS",  # HCL Technologies
    "WIPRO.NS",    # Wipro
    "TECHM.NS",    # Tech Mahindra
    "LTIM.NS",     # L&T Infotech
    "MINDTREE.NS", # Mindtree
    "MPHASIS.NS",  # Mphasis
    "COFORGE.NS",  # Coforge
    "ZENSAR.NS",   # Zensar Technologies
    
    # Banking / Financial Services (10)
    "HDFCBANK.NS", # HDFC Bank
    "ICICIBANK.NS", # ICICI Bank
    "SBIN.NS",     # State Bank of India
    "AXISBANK.NS", # Axis Bank
    "KOTAKBANK.NS", # Kotak Mahindra Bank
    "INDUSINDBK.NS", # IndusInd Bank
    "BANDHANBNK.NS", # Bandhan Bank
    "FEDERALBNK.NS", # Federal Bank
    "IDFCFIRSTB.NS", # IDFC First Bank
    "RBLBANK.NS",  # RBL Bank
    
    # Pharma / Healthcare (10)
    "SUNPHARMA.NS", # Sun Pharma
    "DRREDDY.NS",   # Dr. Reddy's Labs
    "CIPLA.NS",     # Cipla
    "LUPIN.NS",     # Lupin
    "AUROPHARMA.NS", # Aurobindo Pharma
    "TORNTPHARM.NS", # Torrent Pharma
    "GLENMARK.NS",  # Glenmark Pharma
    "CADILAHC.NS",  # Cadila Healthcare
    "DIVISLAB.NS",  # Divi's Labs
    "BIOCON.NS",    # Biocon
    
    # FMCG / Consumer Goods (10)
    "HINDUNILVR.NS", # Hindustan Unilever
    "ITC.NS",       # ITC
    "NESTLEIND.NS", # Nestle India
    "BRITANNIA.NS", # Britannia
    "DABUR.NS",     # Dabur
    "MARICO.NS",    # Marico
    "GODREJCP.NS",  # Godrej Consumer
    "COLPAL.NS",    # Colgate Palmolive
    "EMAMILTD.NS",  # Emami
    "JUBLFOOD.NS",  # Jubilant FoodWorks
    
    # Energy / Oil & Gas (5)
    "RELIANCE.NS",  # Reliance Industries
    "ONGC.NS",      # Oil & Natural Gas Corp
    "IOC.NS",       # Indian Oil Corp
    "BPCL.NS",      # Bharat Petroleum
    "GAIL.NS",      # GAIL India
    
    # Auto / Automobiles (5)
    "MARUTI.NS",    # Maruti Suzuki
    "TATAMOTORS.NS", # Tata Motors
    "M&M.NS",       # Mahindra & Mahindra
    "BAJAJ-AUTO.NS", # Bajaj Auto
    "EICHERMOT.NS", # Eicher Motors
    
    # Metals / Mining (3)
    "TATASTEEL.NS", # Tata Steel
    "JSWSTEEL.NS",  # JSW Steel
    "VEDL.NS",      # Vedanta
    
    # Telecom (1)
    "BHARTIARTL.NS", # Bharti Airtel
    # Note: RELIANCE.NS already included in Energy section (line 60)
    
    # Infrastructure / Engineering (3)
    "LT.NS",        # Larsen & Toubro
    "ADANIPORTS.NS", # Adani Ports
    "ULTRACEMCO.NS", # UltraTech Cement
    
    # Others / Diversified (2)
    "HDFC.NS",      # HDFC (Housing Development Finance Corp)
    "BAJFINANCE.NS", # Bajaj Finance
]

# Validation: Ensure no duplicates
_duplicates = [ticker for ticker in INDIAN_TICKERS if INDIAN_TICKERS.count(ticker) > 1]
if _duplicates:
    raise ValueError(f"Duplicate tickers found in INDIAN_TICKERS: {set(_duplicates)}")

# Alternative: Pure NSE symbols without .NS suffix (if API doesn't need it)
INDIAN_TICKERS_NSE_ONLY = [
    ticker.replace(".NS", "") for ticker in INDIAN_TICKERS
]

# Alternative: BSE format (.BO suffix)
INDIAN_TICKERS_BSE = [
    ticker.replace(".NS", ".BO") for ticker in INDIAN_TICKERS
]

