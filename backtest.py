"""
BACKTEST
--------
This file answers the core question: "If I had followed this rule in the past,
how would my money have done compared to just owning the overall market?"

It builds an equal-weighted portfolio of the picked stocks, tracks its value
over time, and compares it against a benchmark (like the S&P 500).
"""

import numpy as np
import pandas as pd


def portfolio_growth(price_history: pd.DataFrame, picked_tickers: list) -> pd.Series:
    """
    Simulates putting equal amounts of money into each picked stock on day one,
    then tracks the combined value of that basket over time.
    Returns a Series indexed by date, starting at 1.0 (i.e. "1x your money").
    """
    picked_prices = price_history[picked_tickers]
    normalized = picked_prices / picked_prices.iloc[0]  # each stock starts at 1.0
    portfolio_value = normalized.mean(axis=1)  # equal-weighted average
    return portfolio_value


def benchmark_growth(benchmark_prices: pd.Series) -> pd.Series:
    """
    Same idea as portfolio_growth, but for a single benchmark series (e.g. SPY),
    so it can be plotted on the same chart for comparison.
    """
    return benchmark_prices / benchmark_prices.iloc[0]


def performance_stats(growth_series: pd.Series) -> dict:
    """
    Calculates standard risk/return numbers used to judge a strategy:
    - Total return: how much your money grew overall
    - Annualized return: the yearly average growth rate
    - Max drawdown: the worst drop from a peak (how bad did it get at the worst point?)
    - Sharpe ratio: return earned per unit of risk taken (higher = better)
    """
    daily_returns = growth_series.pct_change().dropna()

    total_return = growth_series.iloc[-1] / growth_series.iloc[0] - 1
    num_years = len(growth_series) / 252  # ~252 trading days per year
    annualized_return = (1 + total_return) ** (1 / num_years) - 1

    running_max = growth_series.cummax()
    drawdown = (growth_series - running_max) / running_max
    max_drawdown = drawdown.min()

    sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)

    return {
        "total_return_pct": round(total_return * 100, 2),
        "annualized_return_pct": round(annualized_return * 100, 2),
        "max_drawdown_pct": round(max_drawdown * 100, 2),
        "sharpe_ratio": round(sharpe_ratio, 2),
    }
