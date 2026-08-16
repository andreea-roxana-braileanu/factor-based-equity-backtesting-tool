"""
FACTORS
-------
This file contains the actual "rule" logic: how do we decide which stocks
count as good picks?

- VALUE factor: is the stock cheap relative to earnings/book value?
- MOMENTUM factor: has the stock been going up over the recent past?

Each function gives every stock a score. Higher score = better pick, according
to that rule.
"""

import pandas as pd


def value_scores(fundamentals: pd.DataFrame) -> pd.Series:
    """
    Lower P/E and lower price-to-book = "cheaper" = higher value score.
    We rank stocks so the cheapest gets the highest score.

    IMPORTANT: negative P/E or P/B ratios happen when a company has negative
    earnings or negative book value (common for companies with large stock
    buybacks, like MCD or LOW). A negative ratio is NOT "extremely cheap" --
    it's a sign the ratio itself is meaningless for that company. Those are
    excluded from the ranking (treated as missing) rather than wrongly
    scored as the best possible value picks.
    """
    pe = fundamentals["trailing_pe"].where(fundamentals["trailing_pe"] > 0)
    pb = fundamentals["price_to_book"].where(fundamentals["price_to_book"] > 0)

    pe_rank = pe.rank(ascending=True)   # lower PE = better rank
    pb_rank = pb.rank(ascending=True)   # lower P/B = better rank
    combined = (pe_rank + pb_rank) / 2
    return combined.rank(ascending=False)  # flip so higher score = better pick


def momentum_scores(price_history: pd.DataFrame, lookback_days: int = 126) -> pd.Series:
    """
    Momentum = how much the stock has risen over the last `lookback_days`
    (126 trading days is roughly 6 months).
    Higher recent return = higher momentum score.
    """
    recent_return = price_history.iloc[-1] / price_history.iloc[-lookback_days] - 1
    return recent_return.rank(ascending=False)


def combined_scores(value: pd.Series, momentum: pd.Series) -> pd.Series:
    """
    Averages the two rankings so a stock has to be reasonably good on BOTH
    factors to score well overall -- not just great on one.
    """
    return (value.rank(ascending=True) + momentum.rank(ascending=True)) / 2


def pick_top_stocks(scores: pd.Series, num_stocks: int) -> list:
    """
    Returns the tickers with the best (highest) scores.
    """
    return scores.sort_values(ascending=False).head(num_stocks).index.tolist()


def build_scoreboard(fundamentals: pd.DataFrame, price_history: pd.DataFrame,
                      value_score: pd.Series, momentum_score: pd.Series,
                      final_scores: pd.Series, picked: list,
                      lookback_days: int = 126) -> pd.DataFrame:
    """
    Builds a single, readable table showing EVERY stock's raw numbers and
    scores -- this is the "show your work" table, so you can see exactly
    why each stock was picked or skipped, not just the final winner list.
    """
    momentum_pct = (price_history.iloc[-1] / price_history.iloc[-lookback_days] - 1) * 100

    board = pd.DataFrame({
        "P/E ratio": fundamentals["trailing_pe"].round(2),
        "P/B ratio": fundamentals["price_to_book"].round(2),
        "6mo price change %": momentum_pct.round(2),
        "value score": value_score.round(1),
        "momentum score": momentum_score.round(1),
        "final score": final_scores.round(1),
    })
    board["picked?"] = board.index.map(lambda t: "YES" if t in picked else "")
    return board.sort_values("final score", ascending=False)
