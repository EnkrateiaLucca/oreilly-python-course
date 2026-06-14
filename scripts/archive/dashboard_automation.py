#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas>=2.2",
#   "plotly>=6.0",
# ]
# ///

from __future__ import annotations

import argparse
import json
import random
import sys
import webbrowser
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.io as pio


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.datatables.net/1.13.8/css/jquery.dataTables.min.css" />
  <style>
    :root {{
      --bg: #0b1020;
      --panel: #121933;
      --panel-2: #1a2345;
      --text: #eef2ff;
      --muted: #a8b2d1;
      --border: rgba(255,255,255,0.08);
      --shadow: 0 18px 45px rgba(0,0,0,0.28);
      --radius: 18px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, system-ui, sans-serif;
      background: linear-gradient(180deg, #0a1022 0%, #10182f 100%);
      color: var(--text);
    }}
    .wrap {{ max-width: 1400px; margin: 0 auto; padding: 28px; }}
    .hero {{
      padding: 28px;
      background: linear-gradient(135deg, rgba(80,110,255,0.28), rgba(43,210,255,0.18));
      border: 1px solid var(--border);
      border-radius: 24px;
      box-shadow: var(--shadow);
      margin-bottom: 22px;
    }}
    h1 {{ margin: 0 0 8px; font-size: 2rem; }}
    .subtitle {{ color: var(--muted); margin: 0; line-height: 1.5; }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin: 22px 0;
    }}
    .card {{
      background: rgba(18,25,51,0.92);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 18px;
      box-shadow: var(--shadow);
    }}
    .stat-label {{ color: var(--muted); font-size: 0.9rem; margin-bottom: 6px; }}
    .stat-value {{ font-size: 1.7rem; font-weight: 800; letter-spacing: -0.02em; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      gap: 18px;
    }}
    .panel {{
      grid-column: span 12;
      background: rgba(18,25,51,0.92);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 18px;
      box-shadow: var(--shadow);
    }}
    .panel h2 {{ margin: 0 0 12px; font-size: 1.05rem; }}
    .chart-half {{ grid-column: span 6; }}
    .chart-full {{ grid-column: span 12; }}
    .controls {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 16px;
      align-items: center;
    }}
    .pill {{
      background: var(--panel-2);
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 8px 12px;
      color: var(--muted);
      font-size: 0.92rem;
    }}
    .table-note {{ color: var(--muted); margin: 0 0 10px; }}
    table.dataTable {{ color: var(--text); }}
    table.dataTable thead th, table.dataTable tbody td {{
      background: transparent !important;
      color: var(--text) !important;
      border-bottom: 1px solid rgba(255,255,255,0.06) !important;
    }}
    .dataTables_wrapper .dataTables_filter input,
    .dataTables_wrapper .dataTables_length select {{
      background: #0d1430;
      color: var(--text);
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 10px;
      padding: 8px 10px;
    }}
    .dataTables_wrapper .dataTables_info,
    .dataTables_wrapper .dataTables_length,
    .dataTables_wrapper .dataTables_filter,
    .dataTables_wrapper .dataTables_paginate {{
      color: var(--muted) !important;
      margin-top: 8px;
    }}
    .dataTables_wrapper .dataTables_paginate .paginate_button {{
      color: var(--text) !important;
      border-radius: 10px;
    }}
    @media (max-width: 980px) {{
      .chart-half {{ grid-column: span 12; }}
      .wrap {{ padding: 16px; }}
      h1 {{ font-size: 1.6rem; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>{title}</h1>
      <p class="subtitle">Standalone HTML dashboard generated from a CSV with interactive charts and a searchable data table. Search globally, sort by any column, and inspect the underlying rows directly in the browser.</p>
    </section>

    <section class="stats">
      {stats_html}
    </section>

    <section class="grid">
      <div class="panel chart-half">
        <h2>Revenue over time</h2>
        {chart_revenue}
      </div>
      <div class="panel chart-half">
        <h2>Revenue by region</h2>
        {chart_region}
      </div>
      <div class="panel chart-half">
        <h2>Revenue by category</h2>
        {chart_category}
      </div>
      <div class="panel chart-half">
        <h2>Units sold by channel</h2>
        {chart_channel}
      </div>
      <div class="panel chart-full">
        <h2>Search and explore raw rows</h2>
        <div class="controls">
          <span class="pill">Global search</span>
          <span class="pill">Column sorting</span>
          <span class="pill">Pagination</span>
          <span class="pill">CSV-driven</span>
        </div>
        <p class="table-note">Use the built-in search box to find matching customers, regions, reps, products, or dates.</p>
        {table_html}
      </div>
    </section>
  </div>

  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
  <script src="https://cdn.datatables.net/1.13.8/js/jquery.dataTables.min.js"></script>
  <script>
    $(document).ready(function() {{
      $('#records').DataTable({{
        pageLength: 12,
        responsive: true,
        order: [[0, 'desc']]
      }});
    }});
  </script>
</body>
</html>
"""


def generate_synthetic_csv(output_path: Path, rows: int = 360) -> Path:
    random.seed(42)

    dates = pd.date_range("2025-01-01", periods=180, freq="D")
    regions = ["North", "South", "East", "West", "Central"]
    cities = {
        "North": ["Porto", "Braga", "Viana do Castelo"],
        "South": ["Faro", "Setúbal", "Beja"],
        "East": ["Castelo Branco", "Guarda", "Évora"],
        "West": ["Leiria", "Coimbra", "Aveiro"],
        "Central": ["Lisbon", "Sintra", "Cascais"],
    }
    categories = {
        "Electronics": ["Laptop", "Tablet", "Monitor", "Headphones"],
        "Home": ["Desk Lamp", "Office Chair", "Air Purifier", "Coffee Machine"],
        "Fitness": ["Treadmill", "Yoga Mat", "Dumbbells", "Smart Watch"],
        "Travel": ["Suitcase", "Backpack", "Adapter", "Noise Cancelling Earbuds"],
    }
    channels = ["Online", "Retail", "Partner"]
    segments = ["Consumer", "SMB", "Enterprise"]
    reps = ["Ana", "Bruno", "Carla", "Diogo", "Ines", "Joao", "Marta", "Tiago"]

    price_map = {
        "Laptop": 1200,
        "Tablet": 650,
        "Monitor": 320,
        "Headphones": 180,
        "Desk Lamp": 55,
        "Office Chair": 280,
        "Air Purifier": 210,
        "Coffee Machine": 160,
        "Treadmill": 900,
        "Yoga Mat": 35,
        "Dumbbells": 120,
        "Smart Watch": 260,
        "Suitcase": 140,
        "Backpack": 95,
        "Adapter": 25,
        "Noise Cancelling Earbuds": 220,
    }

    records = []
    for order_id in range(1, rows + 1):
        date = random.choice(dates)
        region = random.choice(regions)
        city = random.choice(cities[region])
        category = random.choice(list(categories))
        product = random.choice(categories[category])
        channel = random.choice(channels)
        segment = random.choice(segments)
        rep = random.choice(reps)
        units = random.randint(1, 12)
        base_price = price_map[product]
        discount = round(random.choice([0, 0.03, 0.05, 0.08, 0.1, 0.12]), 2)
        unit_price = round(base_price * random.uniform(0.92, 1.08), 2)
        revenue = round(units * unit_price * (1 - discount), 2)
        margin = round(random.uniform(0.12, 0.42), 2)
        profit = round(revenue * margin, 2)

        records.append(
            {
                "order_date": date.strftime("%Y-%m-%d"),
                "order_id": f"ORD-{order_id:04d}",
                "region": region,
                "city": city,
                "product_category": category,
                "product": product,
                "sales_channel": channel,
                "customer_segment": segment,
                "sales_rep": rep,
                "units_sold": units,
                "unit_price": unit_price,
                "discount_pct": discount,
                "revenue": revenue,
                "profit_margin_pct": margin,
                "profit": profit,
            }
        )

    df = pd.DataFrame(records).sort_values("order_date")
    df.to_csv(output_path, index=False)
    return output_path


def build_stats(df: pd.DataFrame) -> str:
    stats = [
        ("Rows", f"{len(df):,}"),
        ("Total revenue", f"€{df['revenue'].sum():,.0f}"),
        ("Total profit", f"€{df['profit'].sum():,.0f}"),
        ("Avg order value", f"€{df['revenue'].mean():,.0f}"),
    ]
    return "\n".join(
        f'<div class="card"><div class="stat-label">{label}</div><div class="stat-value">{value}</div></div>'
        for label, value in stats
    )


def plot_div(fig) -> str:
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=30, r=20, t=20, b=30),
        height=380,
    )
    return pio.to_html(fig, include_plotlyjs="cdn", full_html=False)


def build_dashboard(csv_path: Path, html_path: Path, title: str) -> Path:
    df = pd.read_csv(csv_path)
    df["order_date"] = pd.to_datetime(df["order_date"])

    revenue_by_day = df.groupby("order_date", as_index=False)["revenue"].sum()
    revenue_by_region = df.groupby("region", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
    revenue_by_category = df.groupby("product_category", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
    units_by_channel = df.groupby("sales_channel", as_index=False)["units_sold"].sum().sort_values("units_sold", ascending=False)

    fig_revenue = px.line(revenue_by_day, x="order_date", y="revenue", markers=True)
    fig_region = px.bar(revenue_by_region, x="region", y="revenue")
    fig_category = px.pie(revenue_by_category, names="product_category", values="revenue", hole=0.45)
    fig_channel = px.bar(units_by_channel, x="sales_channel", y="units_sold")

    display_df = df.copy()
    display_df["order_date"] = display_df["order_date"].dt.strftime("%Y-%m-%d")
    numeric_cols = ["unit_price", "discount_pct", "revenue", "profit_margin_pct", "profit"]
    for col in numeric_cols:
        display_df[col] = display_df[col].map(lambda x: f"{x:,.2f}")

    table_html = display_df.to_html(
        table_id="records",
        index=False,
        classes="display compact",
        border=0,
        escape=False,
    )

    html = HTML_TEMPLATE.format(
        title=title,
        stats_html=build_stats(df),
        chart_revenue=plot_div(fig_revenue),
        chart_region=plot_div(fig_region),
        chart_category=plot_div(fig_category),
        chart_channel=plot_div(fig_channel),
        table_html=table_html,
    )
    html_path.write_text(html, encoding="utf-8")
    return html_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a browser dashboard from a CSV file.")
    parser.add_argument("csv", nargs="?", help="Path to the input CSV file.")
    parser.add_argument("--html", default="dashboard_output.html", help="Output HTML file path.")
    parser.add_argument("--title", default="CSV Analytics Dashboard", help="Dashboard title.")
    parser.add_argument(
        "--make-example",
        action="store_true",
        help="Generate a synthetic CSV example and use it as the input source.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent

    default_csv = script_dir / "synthetic_sales_data.csv"
    html_path = Path(args.html).expanduser().resolve()

    if args.make_example or (args.csv is None and not default_csv.exists()):
        generate_synthetic_csv(default_csv)
        csv_path = default_csv
    elif args.csv:
        csv_path = Path(args.csv).expanduser().resolve()
        if not csv_path.exists():
            print(f"CSV file not found: {csv_path}", file=sys.stderr)
            return 1
    else:
        csv_path = default_csv

    output = build_dashboard(csv_path=csv_path, html_path=html_path, title=args.title)
    print(json.dumps({"csv": str(csv_path), "html": str(output)}, indent=2))
    webbrowser.open(output.as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
