"""
INTERACTIVE SIMULATOR
----------------------
Run THIS file whenever you want to test "what if I invested $X in stock Y,
Z years ago?" -- it will ask you three simple questions right in the console,
no need to open or edit settings.py.
"""

import datetime
import matplotlib.pyplot as plt

import data_fetch
import simulator
import settings


def main():
    print("=== Investment Simulator ===")
    print("(You can type almost any public company's stock ticker, e.g. AAPL, TSLA, MSFT, KO, NFLX)")

    ticker = input("Which stock ticker? ").strip().upper()
    amount = float(input("How much money would you invest ($)? ").strip())
    years = float(input("How many years back? ").strip())

    start_date = (datetime.date.today() - datetime.timedelta(days=int(365 * years))).isoformat()

    print(f"\nFetching data for {ticker} since {start_date}...")
    tickers = [ticker, settings.BENCHMARK_TICKER]
    prices = data_fetch.get_price_history(tickers, start_date)

    sim_df = simulator.simulate_vs_benchmark(
        prices[ticker],
        prices[settings.BENCHMARK_TICKER],
        amount,
    )
    summary = simulator.summarize_simulation(sim_df, amount)

    print("\n--- Result ---")
    print(f"You invested: ${summary['invested']:.2f}")
    print(f"If you bought {ticker}, it would be worth today: ${summary['final_value_your_stock']:.2f}")
    print(f"If you bought the market (S&P 500) instead, it would be worth: ${summary['final_value_if_market_instead']:.2f}")
    print(f"Profit from {ticker}: ${summary['profit_your_stock']:.2f}")
    print(f"Profit from the market instead: ${summary['profit_if_market_instead']:.2f}")

    plt.figure(figsize=(10, 5))
    plt.plot(sim_df.index, sim_df["your_stock"], label=f"${amount:.0f} in {ticker}")
    plt.plot(sim_df.index, sim_df["benchmark"], label=f"${amount:.0f} in market instead")
    plt.title(f"What if you invested ${amount:.0f} in {ticker}, {years:.0f} years ago?")
    plt.xlabel("Date")
    plt.ylabel("Value ($)")
    plt.legend()
    plt.tight_layout()

    filename = f"simulation_{ticker}_{int(years)}y.png"
    plt.savefig(filename)
    print(f"\nSaved chart: {filename}")


if __name__ == "__main__":
    main()
