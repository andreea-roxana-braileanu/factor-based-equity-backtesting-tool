# Factor-Based Equity Screening & Backtesting Tool

A Python tool that picks stocks using simple quantitative rules ("factors") —
like being cheap relative to earnings, or having risen a lot recently — and
tests how that picking strategy would have performed historically compared to
just owning the overall market. Includes a personal investment simulator that
shows what a chosen dollar amount would be worth today if invested in a
specific stock X years ago, benchmarked against the market.

## How it works, in plain terms

1. Download real historical stock prices and company fundamentals (Yahoo Finance).
2. Save the price data into a SQL database.
3. Score every stock using a rule you choose: "value" (cheap), "momentum"
   (rising), or "both".
4. Pick the top-scoring stocks and simulate holding them, compared to the
   overall market (S&P 500).
5. Separately, simulate: "if I invested $X in [stock] Y years ago, what would
   it be worth today?" — again compared to just investing in the market.
6. Save two charts as PNG images so you can see the results visually.

## Project files

| File | What it does |
|---|---|
| `settings.py` | The only file you usually need to edit — change which stocks, which factor, how far back, how much money, etc. |
| `data_fetch.py` | Downloads real price and fundamentals data from Yahoo Finance |
| `db.py` | Saves and loads price data using SQL (SQLite) |
| `factors.py` | The scoring rules — how "cheap" and "momentum" are calculated |
| `backtest.py` | Simulates the strategy's performance and calculates return/risk stats |
| `simulator.py` | The personal "what if I invested $X" feature |
| `main.py` | Runs everything, in order — **this is the file you run** |

## How to run it

1. Install the required packages (only needs to be done once):
   ```
   pip install -r requirements.txt
   ```
2. Open `settings.py` and change any values you want (stocks, factor,
   amount, years, etc.).
3. Run `main.py`.
4. Check the project folder for two new chart images:
   - `strategy_vs_market.png`
   - `investment_simulation.png`
   Plus printed numbers in the console (total return, Sharpe ratio, max
   drawdown, etc.)

## Ideas for extending it later

- Add more factors (e.g. quality, low volatility)
- Test different time periods and compare results
- Add monthly rebalancing instead of buy-and-hold
- Wrap it in a simple Streamlit app for an interactive on-screen version
- Add the anomaly/data-consistency checks (tying back to Big Four audit experience)
