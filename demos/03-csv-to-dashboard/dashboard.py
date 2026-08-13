# /// script
# requires-python = ">=3.12"
# dependencies = ["pandas", "plotly", "dash"]
# ///
"""Build an interactive web dashboard from ANY CSV file.

Input   -> a path to a CSV file
Process -> auto-detect a date column, a numeric column and a category column,
           then build three interactive plotly charts
Output  -> a local web app at http://127.0.0.1:8050 (open it in your browser)

Run it like:
    uv run demos/03-csv-to-dashboard/dashboard.py SALES.csv

Needs: nothing (no API key). Press Ctrl+C to stop the server.
Read-only: it never modifies your CSV.
"""

import argparse

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Any column with "date" in its name gets parsed into real datetimes so
    # plotly can draw a proper time axis instead of treating dates as text.
    for col in df.columns:
        if "date" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col])
            except (ValueError, TypeError):
                pass  # leave the column as-is if it isn't really dates
    return df


def build_figures(df: pd.DataFrame) -> list:
    """Pick sensible columns automatically and return (title, figure) pairs."""
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    cat_col = next((c for c in df.columns if df[c].dtype == "object"), None)
    date_col = next((c for c in df.columns if "date" in c.lower()), None)

    figures = []
    if date_col and numeric_cols:
        fig = px.line(df.sort_values(date_col), x=date_col, y=numeric_cols[0],
                      title=f"{numeric_cols[0]} over time")
        figures.append(("Time series", fig))
    if numeric_cols:
        fig = px.histogram(df, x=numeric_cols[0],
                           title=f"Distribution of {numeric_cols[0]}")
        figures.append(("Distribution", fig))
    if cat_col and numeric_cols:
        grouped = (df.groupby(cat_col)[numeric_cols[0]].mean()
                   .sort_values(ascending=False).reset_index())
        fig = px.bar(grouped, x=cat_col, y=numeric_cols[0],
                     title=f"Average {numeric_cols[0]} by {cat_col}")
        figures.append(("Category breakdown", fig))

    for _, fig in figures:
        fig.update_layout(template="simple_white", margin=dict(l=40, r=20, t=50, b=40))
    return figures


def build_app(df: pd.DataFrame, title: str) -> Dash:
    app = Dash(__name__)
    card_style = {"background": "white", "padding": "16px",
                  "border": "2px solid black", "borderRadius": "4px"}
    app.layout = html.Div(
        style={"backgroundColor": "#F5F5F5", "minHeight": "100vh",
               "fontFamily": "Helvetica", "padding": "20px"},
        children=[
            html.H1(title, style={"borderBottom": "2px solid black",
                                  "paddingBottom": "6px"}),
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr",
                       "gap": "20px", "alignItems": "start"},
                children=[
                    html.Div(style=card_style,
                             children=[html.H3(name), dcc.Graph(figure=fig)])
                    for name, fig in build_figures(df)
                ],
            ),
        ],
    )
    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve an interactive dashboard for a CSV file.")
    parser.add_argument("csv_path", help="Path to the CSV file, e.g. SALES.csv")
    parser.add_argument("--port", type=int, default=8050,
                        help="Port for the local web server (default: 8050)")
    args = parser.parse_args()

    try:
        df = load_data(args.csv_path)
    except FileNotFoundError:
        print(f"CSV file not found: {args.csv_path}")
        raise SystemExit(1)

    print(f"Loaded {len(df)} rows, {len(df.columns)} columns.")
    print(f"Open http://127.0.0.1:{args.port} in your browser. Ctrl+C stops the server.")
    app = build_app(df, f"Dashboard — {args.csv_path}")
    app.run(debug=False, port=args.port)


if __name__ == "__main__":
    main()
