"""
SETTINGS
--------
This is the only file you should need to edit to change what the project does.
Change a value below, save, then run main.py again to see new results.
"""

# --- Which stocks to look at ---
# A diversified universe across 10 sectors (~60 stocks), so the backtest
# reflects a real, meaningful selection rather than a small handful.
# You can still add/remove tickers freely.
TICKERS = [
    # Technology
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "ADBE", "CRM", "ORCL", "CSCO",
    # Communication / Media
    "NFLX", "DIS", "CMCSA", "TMUS", "VZ", "T",
    # Consumer discretionary
    "TSLA", "HD", "MCD", "NKE", "SBUX", "LOW", "BKNG",
    # Consumer staples
    "PG", "KO", "PEP", "WMT", "COST", "CL", "MDLZ",
    # Financials
    "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "AXP",
    # Healthcare
    "JNJ", "UNH", "PFE", "ABBV", "MRK", "LLY", "TMO",
    # Energy
    "XOM", "CVX", "COP", "SLB",
    # Industrials
    "BA", "CAT", "GE", "HON", "UPS", "RTX",
    # Materials
    "LIN", "APD",
    # Utilities / Real estate
    "NEE", "DUK", "AMT", "PLD",
]

# --- Which factor (rule) to rank stocks by ---
# Options: "value", "momentum", "both"
FACTOR = "both"

# --- How many stocks to pick for the strategy portfolio ---
NUM_STOCKS = 10

# --- How far back to test (in years) ---
START_YEAR = 2019

# --- Benchmark to compare against (the "overall market") ---
BENCHMARK_TICKER = "SPY"  # SPY tracks the S&P 500

# --- Settings for the personal investment simulator ---
SIM_TICKER = "AAPL"
SIM_AMOUNT = 5000        # dollars invested
SIM_YEARS_BACK = 5       # how many years ago you "invested"
