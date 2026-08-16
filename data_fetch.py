"""
DATA FETCH
----------
This file is in charge of getting real stock data from the internet (Yahoo Finance,
via the yfinance package) and handing it back in a clean, usable format.
"""

import yfinance as yf
import pandas as pd


def get_price_history(tickers, start_date, end_date=None):
    """
    Downloads daily closing prices for a list of tickers between two dates.
    Returns a DataFrame: rows = dates, columns = tickers, values = closing price.
    """
    data = yf.download(tickers, start=start_date, end=end_date, progress=False)["Close"]
    # If only one ticker was requested, yfinance returns a Series instead of a
    # DataFrame -- this keeps things consistent either way.
    if isinstance(data, pd.Series):
        data = data.to_frame()
    return data.dropna(how="all")


def get_fundamentals(tickers):
    """
    Grabs a few company fundamentals we need for the "value" factor:
    - trailing P/E ratio (price divided by earnings -- lower can mean "cheaper")
    - price-to-book ratio (price divided by company's book value -- same idea)

    Returns a DataFrame: rows = tickers, columns = the fundamentals.

    If a ticker fails to load (e.g. a temporary Yahoo Finance hiccup), it's
    skipped with a warning instead of crashing the whole run -- that ticker
    simply won't be scored or picked that time.
    """
    rows = []
    total = len(tickers)
    for i, ticker in enumerate(tickers, start=1):
        try:
            info = yf.Ticker(ticker).info
            rows.append({
                "ticker": ticker,
                "trailing_pe": info.get("trailingPE"),
                "price_to_book": info.get("priceToBook"),
            })
        except Exception as e:
            print(f"  [warning] Could not fetch fundamentals for {ticker}, skipping. ({e})")
        if i % 10 == 0 or i == total:
            print(f"  Fetched fundamentals for {i}/{total} tickers...")
    return pd.DataFrame(rows).set_index("ticker")
