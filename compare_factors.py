"""
COMPARE FACTORS
----------------
Runs all three strategies -- value only, momentum only, and both combined --
using the SAME downloaded data (so it's a fair, apples-to-apples test), and
builds one summary table plus one chart showing all of them against the
market, side by side.

Run THIS file whenever you want the full comparison, instead of manually
changing FACTOR in settings.py and re-running main.py three times.
"""

import pandas as pd
import matplotlib.pyplot as plt

import settings
import data_fetch
import db
import factors
import backtest


def main():
    print("--- Downloading data (once, shared across all 3 tests) ---")
    start_date = f"{settings.START_YEAR}-01-01"
    all_tickers = settings.TICKERS + [settings.BENCHMARK_TICKER]
    price_history = data_fetch.get_price_history(all_tickers, start_date)
    db.save_prices(price_history)

    stock_prices = price_history[settings.TICKERS]
    benchmark_prices = price_history[settings.BENCHMARK_TICKER]

    print("\n--- Scoring stocks (value and momentum) ---")
    fundamentals = data_fetch.get_fundamentals(settings.TICKERS)
    value_score = factors.value_scores(fundamentals)
    momentum_score = factors.momentum_scores(stock_prices)
    combined_score = factors.combined_scores(value_score, momentum_score)

    factor_scores = {
        "value": value_score,
        "momentum": momentum_score,
        "both": combined_score,
    }

    benchmark_growth = backtest.benchmark_growth(benchmark_prices)
    benchmark_stats = backtest.performance_stats(benchmark_growth)

    results = []
    growth_curves = {"Market (S&P 500)": benchmark_growth}

    for factor_name, scores in factor_scores.items():
        picked = factors.pick_top_stocks(scores, settings.NUM_STOCKS)
        growth = backtest.portfolio_growth(stock_prices, picked)
        stats = backtest.performance_stats(growth)

        results.append({
            "Strategy": factor_name,
            "Picked stocks": ", ".join(picked),
            "Total return %": stats["total_return_pct"],
            "Annualized return %": stats["annualized_return_pct"],
            "Max drawdown %": stats["max_drawdown_pct"],
            "Sharpe ratio": stats["sharpe_ratio"],
        })
        growth_curves[factor_name.capitalize()] = growth

    results.append({
        "Strategy": "market",
        "Picked stocks": "(whole market benchmark, not picked)",
        "Total return %": benchmark_stats["total_return_pct"],
        "Annualized return %": benchmark_stats["annualized_return_pct"],
        "Max drawdown %": benchmark_stats["max_drawdown_pct"],
        "Sharpe ratio": benchmark_stats["sharpe_ratio"],
    })

    comparison_df = pd.DataFrame(results)

    print("\n--- Comparison: value vs momentum vs both vs market ---")
    print(comparison_df.drop(columns=["Picked stocks"]).to_string(index=False))

    comparison_df.to_csv("factor_comparison.csv", index=False)
    print("\nSaved full table (including picked stocks per strategy): factor_comparison.csv")

    plt.figure(figsize=(10, 6))
    for label, growth in growth_curves.items():
        plt.plot(growth.index, growth.values, label=label)
    plt.title(f"Value vs Momentum vs Both vs Market (since {settings.START_YEAR})")
    plt.xlabel("Date")
    plt.ylabel("Growth of $1")
    plt.legend()
    plt.tight_layout()
    plt.savefig("factor_comparison.png")
    print("Saved chart: factor_comparison.png")


if __name__ == "__main__":
    main()
