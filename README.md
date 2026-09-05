# Factor-Based Equity Screening & Backtesting Tool

A Python + SQL project that picks stocks using classic investing rules, tests whether those rules would have actually beaten the market historically, and includes tools to explore the results interactively.

**Author:** Andreea-Roxana Braileanu

---

## Introduction

This project applies financial analysis concepts — factor investing, backtesting, and risk-adjusted performance — to real market data, using Python and SQL. It was built to combine analytical and technical skills gained through a financial advisory internship (Deloitte) and coursework in statistics and data analysis, and to turn those skills into a working, testable tool rather than a theoretical exercise. Along the way, the project also uncovered and fixed a real methodological flaw (look-ahead bias) in its own backtesting logic — that process, and what it revealed, is documented below.

---

## What it does

In plain terms: the project looks at a group of real companies, ranks them using a rule, picks the top scorers, and tests whether that rule would have actually made money compared to simply owning the overall market — no guessing, no cherry-picking, just real historical data.

**1. Stock screening** — every stock is scored on two factors:
- **Value**: is the stock cheap relative to its earnings (P/E ratio) and net worth (P/B ratio)?
- **Momentum**: has the stock's price been rising over the last 6 months?
- **Both**: averages the value and momentum scores together, so a stock has to rank reasonably well on both to be picked.

**2. Backtesting** — the top-scoring stocks are combined into an equal-weighted portfolio and tested against the S&P 500 (the benchmark) since a chosen start date, reporting total return, annualized return, maximum drawdown, and the Sharpe ratio (return earned per unit of risk taken).

<img width="1000" height="500" alt="image" src="https://github.com/user-attachments/assets/1d049c1a-c553-4b40-90d6-5f0a410ac666" />


**3. Investment simulator** — an interactive tool where anyone can type in a stock, an amount of money, and a number of years, and see what that investment would be worth today versus investing in the market instead. For example, here's what $5,000 in AAPL five years ago would look like versus the market:

<img width="1000" height="500" alt="image" src="https://github.com/user-attachments/assets/eba12c51-fc92-4dcc-b9d9-48f256891716" />

<img width="1000" height="500" alt="image" src="https://github.com/user-attachments/assets/b5d90ac5-9eba-4025-a0d6-d123cc838cc8" />


**4. Transparent scoring** — rather than only showing the final picks, the tool prints and saves a full scoreboard for every stock considered, so the reasoning behind each decision is visible and checkable.

**5. Bias-free rebalancing** — a corrected version of the momentum strategy that re-picks stocks once a year using only the data that would have actually been available at that point in time (see *Findings* below for why this matters).

---

## Technical overview

Built entirely in Python, structured as small, focused modules — one job per file.

| Tool / library | Role |
|---|---|
| Python | Core language |
| yfinance | Downloads real historical prices and fundamentals from Yahoo Finance |
| pandas / numpy | Data handling and financial calculations |
| SQLite (`sqlite3`) | Stores price data using structured SQL queries |
| matplotlib | Generates all charts |

| File | Purpose |
|---|---|
| `settings.py` | All adjustable options — stocks, factor, time period, simulator inputs |
| `data_fetch.py` | Downloads price and fundamentals data, with error handling |
| `db.py` | Saves and loads price data using SQL |
| `factors.py` | Scoring logic (value, momentum) and the results scoreboard |
| `backtest.py` | Performance and risk calculations |
| `simulator.py` / `interactive_simulator.py` | The personal investment calculator |
| `main.py` | Runs one strategy end to end (set by `settings.py`) |
| `compare_factors.py` | Runs value, momentum, and both together, and compares them |
| `rebalanced_backtest.py` | The bias-free, annually rebalanced momentum strategy |
| `usage_guide.html` | A visual quick-start guide (open in any browser) with steps and example tickers |

Data is downloaded fresh from Yahoo Finance every time the project runs — nothing is hardcoded or permanently stored, so results always reflect current market data.

---

## How to run it

Requires Python 3.9 or later. Works from any terminal or Python IDE (PyCharm, VS Code, command line, etc.) — nothing here is tied to a specific editor.

1. Install the required packages (once):
```
   pip install -r requirements.txt
```
2. Open `settings.py` and adjust anything you'd like (stocks, factor, time period, simulator inputs).
3. Run `main.py` for a single strategy, `compare_factors.py` to compare all three at once, or `rebalanced_backtest.py` for the bias-free momentum test.
4. Check the project folder for the generated outputs:
   - Charts: `strategy_vs_market.png`, `investment_simulation.png`, `factor_comparison.png`, `rebalanced_vs_original.png`
   - Tables: `stock_rankings.csv`, `factor_comparison.csv`, `rebalanced_vs_original.csv`
   - Plus the full results printed in the console.

---

## Findings

**Comparing value, momentum, and both combined** (since 2019, 61-stock universe, top 10 picked):

| Strategy | Total return | Annualized return | Max drawdown | Sharpe ratio |
|---|---|---|---|---|
| Value | 180.5% | 14.5% | -39.3% | 0.74 |
| Momentum | 257.2% | 18.2% | -43.4% | 0.73 |
| Both combined | 74.1%–92.0% | 7.6–9.0% | -29.3%–-34.0% | 0.50–0.57 |
| Market (S&P 500) | 246.9% | 17.8% | -33.7% | 0.94 |

None of the three strategies beat the market on a risk-adjusted basis (Sharpe ratio). The most interesting result: **combining value and momentum performed worse than using either factor alone** — averaging two different signals diluted rather than strengthened the result over this period, rather than giving the "best of both worlds" one might expect.

<img width="1000" height="600" alt="image" src="https://github.com/user-attachments/assets/53ed1f42-3cb2-415c-9eaf-3d8b0f3fac50" />


**Finding and fixing a look-ahead bias.** While reviewing the backtest logic, I identified that the original strategy scored stocks using *today's* data (current P/E ratios, current momentum) but tested that selection as if it had been bought years earlier — using information that wouldn't have actually been available at the time. This is a well-known problem in backtesting called look-ahead bias.

This was fully fixable for the momentum factor, since it only requires price history, which is available in full going back to the start date. I rebuilt it to re-pick stocks once a year, using only price data available up to that point in time:

| Momentum strategy | Total return | Annualized return | Max drawdown | Sharpe ratio |
|---|---|---|---|---|
| Original (biased) | 257.2% | 18.2% | -43.4% | 0.73 |
| Rebalanced (bias-free) | 318.6% | 20.7% | -29.3% | **1.01** |
| Market (S&P 500) | 246.9% | 17.8% | -33.7% | 0.94 |

<img width="1000" height="600" alt="image" src="https://github.com/user-attachments/assets/ed6e7d14-fe7f-4d8f-bf89-11dce22995ec" />


The corrected, bias-free version was the only strategy in the whole project to beat the market on every metric — higher return, lower risk, and a Sharpe ratio above 1. It also outperformed its own biased predecessor, which suggests that adapting picks annually to real, current conditions was more effective than a single hindsight-informed pick — a genuinely useful and non-obvious result from fixing the methodology properly instead of leaving it as-is.

I also caught a data-quality issue during this process: a handful of companies (e.g. MCD, LOW) have negative price-to-book ratios due to large stock buybacks, which were initially being mis-ranked as "extremely cheap." The scoring logic now excludes negative ratios rather than misinterpreting them.

---

## Limitations

- **The value factor still has look-ahead bias.** Fixing it would require historical fundamentals data (e.g. "what was Apple's P/E ratio in January 2020?"), which isn't available through the free data source used in this project (Yahoo Finance only provides current fundamentals). This is a known, documented gap rather than a silently ignored one.
- **Survivorship bias.** The 61-stock universe consists of companies that are large and successful today. Companies that existed in 2019 but were later delisted or went bankrupt aren't included, which likely inflates results across the board, including the benchmark.
- **No dividends.** Returns are based on price changes only. Since this applies equally to the strategies and the benchmark, comparisons between them remain fair, but absolute return figures understate what a real investor would have earned.
- **Small rebalancing sample.** The bias-free momentum test is based on 8 yearly rebalance decisions (2019–2026) — a small sample. A different set of rebalance dates or stock universe could shift the result.
- **No transaction costs or taxes.** All calculations assume frictionless, equal-weighted trading.

---

## Possible next steps

- Extend point-in-time rebalancing to the value factor, using a paid fundamentals data provider
- Add a "quality" factor (e.g. return on equity, debt levels)
- Add a sector-concentration check to flag when picks are too clustered in one industry
- Test different rebalancing frequencies (quarterly vs. annual) and different lookback windows for momentum
- Add anomaly and data-consistency checks on the fetched fundamentals (e.g. flagging implausible ratios or missing data) — a natural extension of the data-quality instincts built during my Big Four (Deloitte) audit internship
