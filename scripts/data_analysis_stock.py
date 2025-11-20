#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "pandas>=2.0.0",
#   "plotly>=5.20.0",
# ]
# ///
"""
Generate an interactive stock trading dashboard from a CSV file.

Usage:
    python stock_dashboard.py stock-trading-data.csv
    # or, with uv:
    uv run stock_dashboard.py stock-trading-data.csv

Optional:
    python stock_dashboard.py stock-trading-data.csv -o my_dashboard.html
"""

import argparse
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio


def load_data(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    # Ensure expected columns exist (simple sanity checks)
    required_cols = [
        "Date",
        "Stock Symbol",
        "Open Price",
        "Close Price",
        "Volume",
        "Moving Average (50-day)",
        "RSI (Relative Strength Index)",
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns in CSV: {missing}")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.sort_values(["Stock Symbol", "Date"])
    return df


def build_figures(df: pd.DataFrame):
    symbols = df["Stock Symbol"].unique().tolist()
    first_symbol = symbols[0]

    # 1) Close price over time
    fig_price = px.line(
        df,
        x="Date",
        y="Close Price",
        color="Stock Symbol",
        title="Close Price Over Time",
        labels={
            "Date": "Date",
            "Close Price": "Close Price",
            "Stock Symbol": "Symbol",
        },
    )
    fig_price.update_layout(
        hovermode="x unified",
        legend_title_text="Symbol",
    )

    # 2) Volume over time
    fig_volume = px.line(
    df,
    x="Date",
    y=df["Volume"].rolling(5).mean(),  
    color="Stock Symbol",
    title="Trading Volume (5-Day Rolling Avg)",
    labels={"Date": "Date", "y": "Volume (5-day avg)", "Stock Symbol": "Symbol"},
)
    fig_volume.update_traces(mode="lines")
    fig_volume.update_layout(
        hovermode="x unified",
        legend_title_text="Symbol",
    )

    # 3) Moving average vs close price for first symbol
    df_first = df[df["Stock Symbol"] == first_symbol]

    fig_ma = go.Figure()
    fig_ma.add_trace(
        go.Scatter(
            x=df_first["Date"],
            y=df_first["Close Price"],
            mode="lines",
            name=f"{first_symbol} Close Price",
        )
    )
    fig_ma.add_trace(
        go.Scatter(
            x=df_first["Date"],
            y=df_first["Moving Average (50-day)"],
            mode="lines",
            name=f"{first_symbol} 50-day Moving Avg",
        )
    )
    fig_ma.update_layout(
        title=f"{first_symbol}: Close Price vs 50-day Moving Average",
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode="x unified",
        legend_title_text="Series",
    )

    # 4) RSI over time
    fig_rsi = px.line(
        df,
        x="Date",
        y="RSI (Relative Strength Index)",
        color="Stock Symbol",
        title="RSI Over Time",
        labels={
            "Date": "Date",
            "RSI (Relative Strength Index)": "RSI",
            "Stock Symbol": "Symbol",
        },
    )
    fig_rsi.update_layout(
        hovermode="x unified",
        legend_title_text="Symbol",
        yaxis=dict(range=[0, 100]),
    )

    return fig_price, fig_volume, fig_ma, fig_rsi, first_symbol


def build_dashboard_html(
    df: pd.DataFrame,
    title: str = "Stock Trading Dashboard",
) -> str:
    fig_price, fig_volume, fig_ma, fig_rsi, first_symbol = build_figures(df)

    config = {
        "displaylogo": False,
        "modeBarButtonsToRemove": [
            "select2d",
            "lasso2d",
            "autoScale2d",
        ],
    }

    price_html = pio.to_html(
        fig_price, include_plotlyjs=False, full_html=False, config=config
    )
    volume_html = pio.to_html(
        fig_volume, include_plotlyjs=False, full_html=False, config=config
    )
    ma_html = pio.to_html(
        fig_ma, include_plotlyjs=False, full_html=False, config=config
    )
    rsi_html = pio.to_html(
        fig_rsi, include_plotlyjs=False, full_html=False, config=config
    )

    # Minimal sleek layout with CSS
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {{
      --bg-color: #050816;
      --card-bg: #0b1020;
      --card-border: #1f2937;
      --accent: #38bdf8;
      --accent-soft: rgba(56, 189, 248, 0.15);
      --text-main: #e5e7eb;
      --text-muted: #9ca3af;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: radial-gradient(circle at top left, #0f172a 0, #020617 45%, #000 100%);
      color: var(--text-main);
      min-height: 100vh;
      padding: 32px 24px 40px;
    }}

    .container {{
      max-width: 1280px;
      margin: 0 auto;
    }}

    .header {{
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-bottom: 28px;
    }}

    .title {{
      font-size: 1.9rem;
      font-weight: 700;
      letter-spacing: 0.03em;
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .title-pill {{
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.15em;
      padding: 3px 9px;
      border-radius: 9999px;
      border: 1px solid var(--accent-soft);
      background: linear-gradient(135deg, rgba(56,189,248,0.12), rgba(8,47,73,0.3));
      color: var(--accent);
    }}

    .subtitle {{
      font-size: 0.95rem;
      color: var(--text-muted);
      max-width: 620px;
    }}

    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 10px;
      margin-top: 10px;
    }}

    .pill {{
      padding: 6px 10px;
      font-size: 0.8rem;
      border-radius: 9999px;
      border: 1px solid rgba(148,163,184,0.3);
      color: var(--text-muted);
      display: inline-flex;
      align-items: center;
      gap: 8px;
      white-space: nowrap;
    }}

    .pill-dot {{
      width: 6px;
      height: 6px;
      border-radius: 9999px;
      background-color: var(--accent);
    }}

    .grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr);
      gap: 18px;
    }}

    .grid-bottom {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 18px;
      margin-top: 18px;
    }}

    .card {{
      background: radial-gradient(circle at top left, rgba(15,23,42,0.85), rgba(15,23,42,0.5));
      border-radius: 18px;
      border: 1px solid var(--card-border);
      padding: 14px 12px 10px;
      box-shadow:
        0 18px 40px rgba(0,0,0,0.55),
        0 0 0 1px rgba(15,23,42,0.8);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      position: relative;
      overflow: hidden;
    }}

    .card::before {{
      content: "";
      position: absolute;
      inset: -20%;
      background:
        radial-gradient(circle at top, rgba(56,189,248,0.18), transparent 55%),
        radial-gradient(circle at bottom right, rgba(59,130,246,0.12), transparent 55%);
      opacity: 0.45;
      pointer-events: none;
    }}

    .card-inner {{
      position: relative;
      z-index: 1;
    }}

    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 4px;
      gap: 8px;
    }}

    .card-title {{
      font-size: 0.88rem;
      font-weight: 600;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: #e5e7eb;
    }}

    .card-subtitle {{
      font-size: 0.75rem;
      color: var(--text-muted);
    }}

    .badge {{
      font-size: 0.7rem;
      padding: 2px 7px;
      border-radius: 9999px;
      border: 1px solid rgba(148,163,184,0.35);
      color: var(--text-muted);
    }}

    .chart {{
      margin-top: 6px;
      border-radius: 12px;
      background: rgba(15,23,42,0.9);
      padding: 2px;
    }}

    .hint {{
      font-size: 0.76rem;
      color: var(--text-muted);
      margin-top: 12px;
    }}

    @media (max-width: 900px) {{
      body {{
        padding: 20px 14px 32px;
      }}
      .grid {{
        grid-template-columns: minmax(0, 1fr);
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <header class="header">
      <div class="title">
        <span>{title}</span>
        <span class="title-pill">Interactive</span>
      </div>
      <p class="subtitle">
        Explore price action, trading volume, moving averages and RSI for your stock universe.
        Use the legend to toggle symbols and drag on any chart to zoom into specific periods.
      </p>
      <div class="summary-grid">
        <div class="pill">
          <span class="pill-dot"></span>
          Multi-symbol price &amp; volume
        </div>
        <div class="pill">
          <span class="pill-dot"></span>
          Moving average vs. price ({first_symbol})
        </div>
        <div class="pill">
          <span class="pill-dot"></span>
          RSI for momentum insights
        </div>
        <div class="pill">
          <span class="pill-dot"></span>
          Hover for precise values
        </div>
      </div>
    </header>

    <main>
      <section class="grid">
        <article class="card">
          <div class="card-inner">
            <div class="card-header">
              <div>
                <div class="card-title">Close Price</div>
                <div class="card-subtitle">All symbols · time-series</div>
              </div>
              <span class="badge">Legend: click to isolate</span>
            </div>
            <div class="chart">
              {price_html}
            </div>
          </div>
        </article>

        <article class="card">
          <div class="card-inner">
            <div class="card-header">
              <div>
                <div class="card-title">Trading Volume</div>
                <div class="card-subtitle">Compare activity across symbols</div>
              </div>
              <span class="badge">Bars · grouped</span>
            </div>
            <div class="chart">
              {volume_html}
            </div>
          </div>
        </article>
      </section>

      <section class="grid-bottom">
        <article class="card">
          <div class="card-inner">
            <div class="card-header">
              <div>
                <div class="card-title">Price vs 50-day Moving Avg</div>
                <div class="card-subtitle">{first_symbol} · trend vs. smoothing</div>
              </div>
              <span class="badge">Mean reversion view</span>
            </div>
            <div class="chart">
              {ma_html}
            </div>
          </div>
        </article>

        <article class="card">
          <div class="card-inner">
            <div class="card-header">
              <div>
                <div class="card-title">RSI (Relative Strength Index)</div>
                <div class="card-subtitle">Momentum across symbols</div>
              </div>
              <span class="badge">0–100 band</span>
            </div>
            <div class="chart">
              {rsi_html}
            </div>
            <p class="hint">
              Tip: Watch for RSI extremes (e.g. &gt;70 or &lt;30) alongside price and volume
              for potential overbought/oversold signals.
            </p>
          </div>
        </article>
      </section>
    </main>
  </div>
</body>
</html>
"""
    return html


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an interactive stock trading dashboard from a CSV file."
    )
    parser.add_argument(
        "input_csv",
        type=str,
        help="Path to the stock trading data CSV file.",
    )
    parser.add_argument(
        "-o",
        "--output-html",
        type=str,
        default="stock_dashboard.html",
        help="Path to the output HTML file (default: stock_dashboard.html).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input_csv)
    output_path = Path(args.output_html)

    if not input_path.exists():
        raise SystemExit(f"Input CSV not found: {input_path}")

    df = load_data(input_path)
    html = build_dashboard_html(df)

    output_path.write_text(html, encoding="utf-8")
    print(f"Dashboard written to: {output_path.resolve()}")


if __name__ == "__main__":
    main()