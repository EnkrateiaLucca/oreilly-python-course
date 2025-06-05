# /// script
# python = ">=3.8"
# dependencies = [
#   "pandas",
#   "matplotlib",
# ]
# ///

import pandas as pd
import matplotlib.pyplot as plt

def plot_stock_trend(csv_path: str, stock_symbol: str, output_path: str = "stock_trend_plot.png"):
    # Load data
    df = pd.read_csv(csv_path)
    df['Date'] = pd.to_datetime(df['Date'])

    # Filter by stock symbol
    stock_df = df[df['Stock Symbol'] == stock_symbol]

    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(stock_df['Date'], stock_df['Close Price'], label='Close Price')
    plt.plot(stock_df['Date'], stock_df['Moving Average (50-day)'], label='50-day MA', linestyle='--')
    plt.title(f'{stock_symbol} Stock Price Over Time')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.xticks(rotation=45)

    # Save to file
    plt.savefig(output_path)
    print(f"✅ Plot saved to {output_path}")

if __name__ == "__main__":
    # Replace this with your actual file path if needed
    csv_file = "/Users/greatmaster/Desktop/projects/oreilly-live-trainings/oreilly-python-course/notebooks/assets/stock-trading-data.csv"
    stock = "AAPL"
    plot_stock_trend(csv_file, stock)