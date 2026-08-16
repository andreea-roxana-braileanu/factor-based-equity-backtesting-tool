"""
SIMULATOR
---------
This is the friendly "what if I had invested?" feature.
You give it a dollar amount, a stock, and how many years back -- it tells you
what that money would be worth today, and shows the ride it took to get there.
"""

import pandas as pd


def simulate_investment(price_history: pd.Series, amount: float) -> pd.Series:
    """
    price_history: daily closing prices for ONE stock, oldest date first.
    amount: how much money was invested on the very first date.

    Returns a Series of the investment's dollar value over time.
    """
    shares_bought = amount / price_history.iloc[0]
    value_over_time = price_history * shares_bought
    return value_over_time


def simulate_vs_benchmark(stock_prices: pd.Series, benchmark_prices: pd.Series, amount: float) -> pd.DataFrame:
    """
    Runs the same simulation for the chosen stock AND a benchmark (e.g. SPY),
    so you can see side by side whether picking that stock beat "just owning the market."
    """
    stock_value = simulate_investment(stock_prices, amount)
    benchmark_value = simulate_investment(benchmark_prices, amount)

    result = pd.DataFrame({
        "your_stock": stock_value,
        "benchmark": benchmark_value,
    })
    return result


def summarize_simulation(sim_df: pd.DataFrame, amount: float) -> dict:
    """
    Turns the simulation into a few plain-English numbers.
    """
    final_stock = sim_df["your_stock"].iloc[-1]
    final_benchmark = sim_df["benchmark"].iloc[-1]

    return {
        "invested": amount,
        "final_value_your_stock": round(final_stock, 2),
        "final_value_if_market_instead": round(final_benchmark, 2),
        "profit_your_stock": round(final_stock - amount, 2),
        "profit_if_market_instead": round(final_benchmark - amount, 2),
    }
