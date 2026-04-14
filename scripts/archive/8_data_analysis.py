# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pandas>=2.0",
#     "matplotlib>=3.7",
# ]
# ///
"""
Usage:
  uv run pdf_analysis.py /path/to/stock-trading-data.csv
  (If no path is given, it tries './stock-trading-data.csv')

Output:
  ./stock_analysis_report.pdf
"""

# -----------------------------
# Imports & CLI argument parsing
# -----------------------------
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

# -----------------------------
# Parse input CSV path (positional, optional)
# -----------------------------
parser = argparse.ArgumentParser(description="Generate a professional PDF dashboard report for stock trading data.")
parser.add_argument("csv", nargs="?", default="stock-trading-data.csv",
                    help="Path to the input CSV (default: ./stock-trading-data.csv)")
parser.add_argument("--out", default="stock_analysis_report.pdf",
                    help="Output PDF filename (default: stock_analysis_report.pdf)")
args = parser.parse_args()
csv_path = Path(args.csv)
out_pdf = Path(args.out)

# -----------------------------
# Theme & helper formatters
# -----------------------------
# A lightweight, modern visual theme (fonts, grids, colors, spacing).
mpl.rcParams.update({
    "figure.dpi": 120,
    "savefig.dpi": 300,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#E6E6E6",
    "axes.grid": True,
    "grid.color": "#ECECEC",
    "grid.linewidth": 0.8,
    "grid.alpha": 1.0,
    "axes.titleweight": "bold",
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "legend.frameon": False,
    "font.family": "DejaVu Sans",
    "axes.prop_cycle": mpl.cycler(color=[
        "#0F609B", "#EF6C00", "#2F855A", "#805AD5", "#D53F8C", "#2D3748"
    ]),
})

def fmt_currency(x, _pos=None):  # Price axis
    return f"${x:,.0f}" if abs(x) >= 1 else f"${x:,.2f}"

def fmt_percent(x, _pos=None):   # Return axis
    return f"{x:.0f}%"

def fmt_thousands(x, _pos=None): # Volume axis
    # Show in millions when large
    if abs(x) >= 1_000_000:
        return f"{x/1_000_000:.1f}M"
    if abs(x) >= 1_000:
        return f"{x/1_000:.0f}K"
    return f"{x:.0f}"

def date_axis(ax):
    """Concise, professional date formatting with quarterly tick preference."""
    locator = mdates.AutoDateLocator(minticks=5, maxticks=8)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    for label in ax.get_xticklabels():
        label.set_rotation(0)
        label.set_ha("center")

# -----------------------------
# Load data & light validation
# -----------------------------
required_cols = [
    "Date",
    "Stock Symbol",
    "Open Price",
    "Close Price",
    "Volume",
    "Moving Average (50-day)",
    "RSI (Relative Strength Index)"
]
df = pd.read_csv(csv_path)
missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"])
df = df.sort_values(["Stock Symbol", "Date"]).reset_index(drop=True)

# Pick primary ticker (AAPL if present, else first by alphabetical)
tickers = sorted(df["Stock Symbol"].unique().tolist())
primary = "AAPL" if "AAPL" in tickers else tickers[0]
primary_df = df[df["Stock Symbol"] == primary].copy()

# Convenience metrics
returns = df.groupby("Stock Symbol").apply(
    lambda x: (x["Close Price"].iloc[-1] / max(x["Close Price"].iloc[0], 1e-9) - 1) * 100
).sort_values(ascending=False)
avg_volume = df.groupby("Stock Symbol")["Volume"].mean().sort_values(ascending=False)

# -----------------------------
# Page decorations: header/footer
# -----------------------------
def decorate_page(fig, title_left: str, title_right: str, page_number: int | None = None):
    """Adds a subtle header and a footer with page number."""
    # Header bar
    fig.text(0.055, 0.985, title_left, ha="left", va="top", fontsize=10, color="#4A5568")
    fig.text(0.945, 0.985, title_right, ha="right", va="top", fontsize=10, color="#4A5568")
    # Footer line + page
    fig.text(0.5, 0.018, "Generated with Python • pandas • matplotlib", ha="center", va="bottom", fontsize=8, color="#A0AEC0")
    if page_number is not None:
        fig.text(0.98, 0.018, f"{page_number}", ha="right", va="bottom", fontsize=8, color="#A0AEC0")

# -----------------------------
# Helper: clean "text page" with real hierarchy
# -----------------------------
def add_text_page(pdf, title: str, blocks: list[tuple[str, list[str]]], subtitle: str | None = None, page_num: int | None = None):
    """
    Renders a simple, tidy 'document-like' page.
    blocks: [(heading, [bullet lines...]), ...]
    """
    fig = plt.figure(figsize=(10.5, 7.2), layout="constrained")
    gs = fig.add_gridspec(nrows=12, ncols=12)
    ax = fig.add_subplot(gs[:, :])
    ax.axis("off")

    # Title & optional subtitle
    y = 0.94
    ax.text(0.02, y, title, fontsize=22, fontweight="bold", color="#1A202C", va="top")
    if subtitle:
        ax.text(0.02, y-0.06, subtitle, fontsize=11, color="#4A5568", va="top")
    y -= 0.10

    # Content blocks
    for heading, lines in blocks:
        ax.text(0.02, y, heading, fontsize=14, fontweight="bold", color="#2D3748", va="top")
        y -= 0.045
        for line in lines:
            ax.text(0.04, y, f"•  {line}", fontsize=11, color="#2D3748", va="top")
            y -= 0.035
        y -= 0.02  # space between blocks

    decorate_page(fig,
                  title_left="Stock Trading Dashboard Report",
                  title_right=f"Universe: {', '.join(tickers)}",
                  page_number=page_num)
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

# -----------------------------
# Charts
# -----------------------------
def page_price_and_ma(pdf, data: pd.DataFrame, page_num: int | None = None):
    fig = plt.figure(figsize=(10.5, 6.8), layout="constrained")
    ax = fig.add_subplot(111)

    ax.plot(data["Date"], data["Close Price"], linewidth=2.2, label="Close")
    ax.plot(data["Date"], data["Moving Average (50-day)"], linewidth=2.0, linestyle="--", label="50-day MA", alpha=0.9)

    ax.set_title(f"{primary} — Closing Price & 50-day Moving Average")
    ax.set_ylabel("Price")
    ax.yaxis.set_major_formatter(FuncFormatter(fmt_currency))
    date_axis(ax)
    ax.grid(True, which="major")
    ax.legend(ncols=2, frameon=False, loc="upper left")

    # Light band to guide the eye around recent data
    if len(data) > 5:
        last_dt = data["Date"].iloc[-1]
        first_dt = data["Date"].iloc[max(0, len(data)-60)]
        ax.axvspan(first_dt, last_dt, alpha=0.04, color="#3182CE")

    decorate_page(fig,
                  title_left="1) Price & Trend",
                  title_right=f"Window: {data['Date'].min().date()} → {data['Date'].max().date()}",
                  page_number=page_num)
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

def page_rsi(pdf, data: pd.DataFrame, page_num: int | None = None):
    fig = plt.figure(figsize=(10.5, 5.2), layout="constrained")
    ax = fig.add_subplot(111)

    ax.plot(data["Date"], data["RSI (Relative Strength Index)"], linewidth=1.8, label="RSI")
    ax.fill_between(data["Date"], 70, 100, alpha=0.06, label="Overbought")
    ax.fill_between(data["Date"], 0, 30, alpha=0.06, label="Oversold")

    ax.axhline(70, linestyle="--", linewidth=1, color="#E53E3E")
    ax.axhline(30, linestyle="--", linewidth=1, color="#38A169")
    ax.set_ylim(0, 100)
    ax.set_title(f"{primary} — RSI (Relative Strength Index)")
    ax.set_ylabel("RSI")
    date_axis(ax)
    ax.legend(ncols=3, frameon=False, loc="upper left")

    decorate_page(fig, title_left="2) Momentum (RSI)", title_right="Reference: 30 / 70 bands", page_number=page_num)
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

def page_total_returns(pdf, ret: pd.Series, page_num: int | None = None):
    fig = plt.figure(figsize=(10.5, 6.0), layout="constrained")
    ax = fig.add_subplot(111)

    ret_sorted = ret.sort_values(ascending=False)
    bars = ax.bar(ret_sorted.index, ret_sorted.values)

    ax.set_title("Total Return by Stock (%)")
    ax.set_ylabel("Return (%)")
    ax.yaxis.set_major_formatter(FuncFormatter(fmt_percent))
    ax.set_xlabel("Stock Symbol")
    ax.grid(axis="y")

    # Annotate bars with values
    for b in bars:
        ax.text(b.get_x() + b.get_width()/2, b.get_height(),
                f"{b.get_height():.0f}%", ha="center", va="bottom", fontsize=9)

    decorate_page(fig, title_left="3) Cross-Section Performance", title_right="First→Last available close", page_number=page_num)
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

def page_avg_volume(pdf, volume_mean: pd.Series, page_num: int | None = None):
    fig = plt.figure(figsize=(10.5, 6.0), layout="constrained")
    ax = fig.add_subplot(111)

    vol_sorted = volume_mean.sort_values(ascending=False)
    bars = ax.bar(vol_sorted.index, vol_sorted.values)

    ax.set_title("Average Daily Trading Volume by Stock")
    ax.set_ylabel("Average Volume")
    ax.yaxis.set_major_formatter(FuncFormatter(fmt_thousands))
    ax.set_xlabel("Stock Symbol")
    ax.grid(axis="y")

    for b in bars:
        ax.text(b.get_x() + b.get_width()/2, b.get_height(),
                fmt_thousands(b.get_height()), ha="center", va="bottom", fontsize=9)

    decorate_page(fig, title_left="4) Liquidity Snapshot", title_right="Higher volume → easier execution (usually)", page_number=page_num)
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

# -----------------------------
# Build the PDF report
# -----------------------------
with PdfPages(out_pdf) as pdf:
    page = 1

    # Cover / Overview
    add_text_page(
        pdf,
        title="Stock Trading Dashboard Report",
        subtitle=f"Time window: {df['Date'].min().date()} → {df['Date'].max().date()}",
        blocks=[
            ("Universe",
             [", ".join(tickers)]),
            ("What’s inside",
             [
                 "1) Price & 50-day Moving Average (primary ticker)",
                 "2) RSI momentum with overbought/oversold zones",
                 "3) Cross-section: Total Return by Stock (%)",
                 "4) Cross-section: Average Daily Trading Volume",
             ]),
            ("How to read",
             [
                 "Price vs. 50-day MA highlights medium-term trend shifts.",
                 "RSI >70 ≈ overbought, <30 ≈ oversold (context matters).",
                 "Total return = last close / first close − 1.",
                 "Higher average volume often implies tighter spreads.",
             ]),
        ],
        page_num=page,
    ); page += 1

    # 1) Price & 50-day MA (primary)
    add_text_page(
        pdf,
        title=f"1) {primary} — Closing Price & 50-day Moving Average",
        blocks=[
            ("Why it matters",
             ["Trend + price context improves timing and risk framing."]),
            ("Reading tips",
             ["Watch crossovers and persistent gaps between price and MA.",
              "Recent period highlighted to focus attention."]),
        ],
        page_num=page,
    ); page += 1
    page_price_and_ma(pdf, primary_df, page_num=page); page += 1

    # 2) RSI
    add_text_page(
        pdf,
        title=f"2) {primary} — RSI (Relative Strength Index)",
        blocks=[
            ("Why it matters",
             ["Momentum oscillator that can signal exhaustion or reversals."]),
            ("Reading tips",
             ["Zones shaded for quick scan; combine with price action."]),
        ],
        page_num=page,
    ); page += 1
    page_rsi(pdf, primary_df, page_num=page); page += 1

    # 3) Total Return
    add_text_page(
        pdf,
        title="3) Total Return by Stock (%)",
        blocks=[
            ("Why it matters",
             ["Cross-section snapshot to see relative winners/laggards."]),
            ("Method",
             ["Simple first→last close change (unadjusted for dividends/splits)."]),
        ],
        page_num=page,
    ); page += 1
    page_total_returns(pdf, returns, page_num=page); page += 1

    # 4) Average Volume
    add_text_page(
        pdf,
        title="4) Average Daily Trading Volume by Stock",
        blocks=[
            ("Why it matters",
             ["Liquidity affects execution quality, slippage, and viability of strategies."]),
            ("Reading tips",
             ["Consider volume alongside volatility and market microstructure."]),
        ],
        page_num=page,
    ); page += 1
    page_avg_volume(pdf, avg_volume, page_num=page); page += 1

print(f"Report written to: {out_pdf.resolve()}")