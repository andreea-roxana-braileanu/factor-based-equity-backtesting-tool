"""
DATABASE
--------
This file saves the price data into a small SQL database file (quant_project.db)
so you have a real SQL component in the project, and so you don't have to
re-download data from the internet every single time you run the code.
"""

import sqlite3
import pandas as pd

DB_PATH = "quant_project.db"


def save_prices(price_df: pd.DataFrame):
    """
    Saves a wide price DataFrame (dates x tickers) into a SQL table called 'prices',
    in a tidy format: one row per (date, ticker, price).
    """
    long_df = price_df.reset_index().melt(id_vars=price_df.index.name or "index",
                                           var_name="ticker", value_name="close")
    long_df.columns = ["date", "ticker", "close"]

    conn = sqlite3.connect(DB_PATH)
    long_df.to_sql("prices", conn, if_exists="replace", index=False)
    conn.close()


def load_prices(ticker: str = None) -> pd.DataFrame:
    """
    Loads price data back out of the SQL database.
    If a ticker is given, only that ticker's rows are returned (this is a real
    SQL query using a WHERE clause).
    """
    conn = sqlite3.connect(DB_PATH)
    if ticker:
        query = "SELECT date, ticker, close FROM prices WHERE ticker = ? ORDER BY date"
        df = pd.read_sql(query, conn, params=(ticker,), parse_dates=["date"])
    else:
        query = "SELECT date, ticker, close FROM prices ORDER BY date"
        df = pd.read_sql(query, conn, parse_dates=["date"])
    conn.close()
    return df
