# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pandas",
#     "numpy",
#     "openpyxl",
# ]
# ///

import os
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Create input folder
input_dir = "./input"
os.makedirs(input_dir, exist_ok=True)

# Script expects columns A:Q → 17 columns total
required_cols = [
    "Date",
    "Stock Symbol",
    "Close Price",
    "Moving Average (50-day)",
    "RSI (Relative Strength Index)",
    "MACD",
    "Signal Line",
]

# Create 10 extra dummy columns so total = 17 (A→Q)
extra_cols = [f"Extra_{i}" for i in range(1, 17 - len(required_cols) + 1)]

all_cols = required_cols + extra_cols

start_date = datetime.today() - timedelta(days=30)
symbols = ["AAPL", "MSFT"]

for file_index in range(1, 3):
    data = []
    for symbol in symbols:
        date = start_date
        for i in range(30):
            row = {
                "Date": date,
                "Stock Symbol": symbol,
                "Close Price": 150 + i + (file_index * 2),
                "Moving Average (50-day)": 148 + i,
                "RSI (Relative Strength Index)": 40 + (i % 20),
                "MACD": 1.2 + (i * 0.05),
                "Signal Line": 1.0 + (i * 0.04),
            }
            # add empty columns
            for col in extra_cols:
                row[col] = np.nan
            data.append(row)
            date += timedelta(days=1)

    df = pd.DataFrame(data, columns=all_cols)
    df.to_excel(os.path.join(input_dir, f"sample_data_{file_index}.xlsx"), index=False)

input_dir