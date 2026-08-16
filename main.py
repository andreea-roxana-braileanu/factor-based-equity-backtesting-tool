"""
MAIN
----
This is the file you actually run. It uses everything else in the project:
  1. Downloads real stock data
  2. Saves it into a SQL database
  3. Scores and picks stocks using your chosen factor rule (settings.py)
  4. Backtests that pick vs. the market
  5. Runs the personal investment simulator
  6. Draws charts for both

To change what it does, edit settings.py -- you should not need to change
anything in this file.
"""

import datetime
import matplotlib.pyplot as plt

import settings
import data_fetch
import db
import factors
import backtest
import simulator


def run_factor_strategy():
    print("\n--- STEP 1: Downloading price history ---")
    start_date = f"{settings.START_YEAR}-01-01"
    all_tickers = settings.TICKERS + [settings.BENCHMARK_TICKER]
    price_history = data_fetch.get_price_history(all_tickers, start_date)

    print("--- STEP 2: Saving prices to SQL database ---")
    db.save_prices(price_history)

    print("--- STEP 3: Scoring stocks using factor:", settings.FACTOR, "---")
    stock_prices = price_history[settings.TICKERS]

    if settings.FACTOR in ("value", "both"):
        fundamentals = data_fetch.get_fundamentals(settings.TICKERS)
        value_score = factors.value_scores(fundamentals)

    if settings.FACTOR in ("momentum", "both"):
        momentum_score = factors.momentum_scores(stock_prices)

    if settings.FACTOR == "value":
        final_scores = value_score
    elif settings.FACTOR == "momentum":
        final_scores = momentum_score
    else:  # both
        final_scores = factors.combined_scores(value_score, momentum_score)

    picked = factors.pick_top_stocks(final_scores, settings.NUM_STOCKS)
    print("Picked stocks:", picked)

    print("--- STEP 4: Backtesting picked stocks vs benchmark ---")
    portfolio_value = backtest.portfolio_growth(stock_prices, picked)
    benchmark_value = backtest.benchmark_growth(price_history[settings.BENCHMARK_TICKER])

    portfolio_stats = backtest.performance_stats(portfolio_value)
    benchmark_stats = backtest.performance_stats(benchmark_value)

    print("\nStrategy performance:", portfolio_stats)
    print("Benchmark (market) performance:", benchmark_stats)

    plt.figure(figsize=(10, 5))
    plt.plot(portfolio_value.index, portfolio_value.values, label="Factor Strategy")
    plt.plot(benchmark_value.index, benchmark_value.values, label=f"Benchmark ({settings.BENCHMARK_TICKER})")
    plt.title(f"Factor Strategy ({settings.FACTOR}) vs Market")
    plt.xlabel("Date")
    plt.ylabel("Growth of $1")
    plt.legend()
    plt.tight_layout()
    plt.savefig("strategy_vs_market.png")
    print("Saved chart: strategy_vs_market.png")


def run_investment_simulator():
    print("\n--- Running personal investment simulator ---")
    years_back = settings.SIM_YEARS_BACK
    start_date = (datetime.date.today() - datetime.timedelta(days=365 * years_back)).isoformat()

    tickers = [settings.SIM_TICKER, settings.BENCHMARK_TICKER]
    prices = data_fetch.get_price_history(tickers, start_date)

    sim_df = simulator.simulate_vs_benchmark(
        prices[settings.SIM_TICKER],
        prices[settings.BENCHMARK_TICKER],
        settings.SIM_AMOUNT,
    )
    summary = simulator.summarize_simulation(sim_df, settings.SIM_AMOUNT)
    print(summary)

    plt.figure(figsize=(10, 5))
    plt.plot(sim_df.index, sim_df["your_stock"], label=f"${settings.SIM_AMOUNT} in {settings.SIM_TICKER}")
    plt.plot(sim_df.index, sim_df["benchmark"], label=f"${settings.SIM_AMOUNT} in market instead")
    plt.title(f"What if you invested ${settings.SIM_AMOUNT} in {settings.SIM_TICKER}, {years_back} years ago?")
    plt.xlabel("Date")
    plt.ylabel("Value ($)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("investment_simulation.png")
    print("Saved chart: investment_simulation.png")


if __name__ == "__main__":
    run_factor_strategy()
    run_investment_simulator()
