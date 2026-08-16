"""
REBALANCED BACKTEST (momentum only, bias-free)
------------------------------------------------
The regular backtest in main.py has a subtle but important flaw: it scores
stocks using TODAY's data, then pretends that portfolio was bought years ago.
That's "look-ahead bias" -- using future information to make a past decision.

This file fixes that, for the momentum factor specifically, by actually
re-picking stocks once a year, using ONLY the price history that existed up
to that point in time. Each year's decision only ever "sees" what a real
investor could have seen on that actual date.

NOTE ON SCOPE: this fix only covers the MOMENTUM factor, because momentum only
needs price history, which we have in full. The VALUE factor (P/E, P/B) would
need historical fundamentals data (e.g. "what was Apple's P/E in Jan 2020?"),
which isn't available through the free Yahoo Finance data used in this project.
That's documented as a known limitation rather than silently ignored.
"""

import pandas as pd
import matplotlib.pyplot as plt

import settings
import data_fetch
import factors
import backtest


def get_rebalance_dates(price_index: pd.DatetimeIndex, start_year: int) -> list:
    """
    Returns one trading date per year (the first available trading day on or
    after Jan 1 of that year) -- these are the points in time where the
    portfolio gets re-picked.
    """
    dates = []
    last_year = price_index[-1].year
    for year in range(start_year, last_year + 1):
        candidates = price_index[price_index >= pd.Timestamp(f"{year}-01-01")]
        if len(candidates) > 0:
            dates.append(candidates[0])
    return dates


def run_rebalanced_momentum(price_history: pd.DataFrame, tickers: list,
                             start_year: int, num_stocks: int,
                             lookback_days: int = 126) -> pd.Series:
    """
    Simulates holding a momentum portfolio that gets re-picked once a year,
    using only price data available up to each rebalance date -- no
    look-ahead bias.

    Returns one continuous growth series (starting at 1.0) spanning the
    whole period, stitched together from each year's segment.
    """
    stock_prices = price_history[tickers]
    rebalance_dates = get_rebalance_dates(stock_prices.index, start_year)

    combined_index = []
    combined_values = []
    running_value = 1.0  # this is what makes each new segment continue from
                          # where the last one left off, instead of resetting

    for i, reb_date in enumerate(rebalance_dates):
        # Only use price history UP TO this rebalance date to make the pick
        # -- this is the key fix: no peeking at data from after this date.
        history_so_far = stock_prices.loc[:reb_date]

        if len(history_so_far) < lookback_days + 1:
            # Not enough history yet to calculate 6-month momentum -- skip
            # this year rather than guess.
            continue

        scores = factors.momentum_scores(history_so_far, lookback_days=lookback_days)
        picks = factors.pick_top_stocks(scores, num_stocks)

        # Hold these picks until the next rebalance date (or to the end of
        # the data, for the final segment)
        next_date = rebalance_dates[i + 1] if i + 1 < len(rebalance_dates) else stock_prices.index[-1]
        segment_prices = stock_prices.loc[reb_date:next_date, picks].dropna(how="all")

        if segment_prices.empty or len(segment_prices) < 2:
            continue

        segment_growth = segment_prices / segment_prices.iloc[0]      # this segment starts at 1.0
        segment_portfolio = segment_growth.mean(axis=1)               # equal-weighted
        scaled_segment = segment_portfolio * running_value            # continue from last segment's ending value

        # Avoid duplicating the boundary date between segments
        start_idx = 1 if combined_values else 0
        combined_index.extend(scaled_segment.index[start_idx:])
        combined_values.extend(scaled_segment.values[start_idx:])

        running_value = scaled_segment.iloc[-1]

        print(f"  Rebalanced on {reb_date.date()}: picked {picks}")

    return pd.Series(combined_values, index=combined_index)


def main():
    print("--- Downloading price history ---")
    # Download an extra year before START_YEAR so the very first rebalance
    # has enough history to calculate 6-month momentum.
    buffer_start = f"{settings.START_YEAR - 1}-01-01"
    all_tickers = settings.TICKERS + [settings.BENCHMARK_TICKER]
    price_history = data_fetch.get_price_history(all_tickers, buffer_start)

    print("\n--- Running bias-free, annually rebalanced momentum strategy ---")
    rebalanced_growth = run_rebalanced_momentum(
        price_history, settings.TICKERS, settings.START_YEAR, settings.NUM_STOCKS
    )

    print("\n--- Running the ORIGINAL (single-pick, has look-ahead bias) momentum strategy for comparison ---")
    stock_prices_full = price_history[settings.TICKERS]
    original_scores = factors.momentum_scores(stock_prices_full)
    original_picks = factors.pick_top_stocks(original_scores, settings.NUM_STOCKS)
    original_growth = backtest.portfolio_growth(
        stock_prices_full.loc[f"{settings.START_YEAR}-01-01":], original_picks
    )

    benchmark_growth = backtest.benchmark_growth(
        price_history[settings.BENCHMARK_TICKER].loc[f"{settings.START_YEAR}-01-01":]
    )

    rebalanced_stats = backtest.performance_stats(rebalanced_growth)
    original_stats = backtest.performance_stats(original_growth)
    benchmark_stats = backtest.performance_stats(benchmark_growth)

    print("\n--- Results: bias-free rebalanced vs original (biased) vs market ---")
    comparison = pd.DataFrame([
        {"Strategy": "Momentum (rebalanced, bias-free)", **rebalanced_stats},
        {"Strategy": "Momentum (original, has look-ahead bias)", **original_stats},
        {"Strategy": "Market (S&P 500)", **benchmark_stats},
    ])
    print(comparison.to_string(index=False))
    comparison.to_csv("rebalanced_vs_original.csv", index=False)
    print("\nSaved: rebalanced_vs_original.csv")

    plt.figure(figsize=(10, 6))
    plt.plot(rebalanced_growth.index, rebalanced_growth.values, label="Momentum (rebalanced, bias-free)")
    plt.plot(original_growth.index, original_growth.values, label="Momentum (original, has look-ahead bias)")
    plt.plot(benchmark_growth.index, benchmark_growth.values, label="Market (S&P 500)")
    plt.title("Bias-free rebalancing vs the original single-pick momentum strategy")
    plt.xlabel("Date")
    plt.ylabel("Growth of $1")
    plt.legend()
    plt.tight_layout()
    plt.savefig("rebalanced_vs_original.png")
    print("Saved chart: rebalanced_vs_original.png")


if __name__ == "__main__":
    main()
