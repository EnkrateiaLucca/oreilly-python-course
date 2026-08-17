# /// script
# requires-python = ">=3.12"
# dependencies = ["pandas", "plotly", "dash", "openai", "python-dotenv"]
# ///
"""Turn ANY CSV into an interactive dashboard — and, with --explain, an AI read on it.

This demo lives on the boundary between the two halves of the course:
  * DETERMINISTIC Python cleans the data and draws the charts (exact, repeatable)
  * AI JUDGEMENT reads the numbers and tells you what's interesting (fuzzy, useful)
The charts you can trust to the cell; the explanation is a lead to verify, not gospel.

Input   -> a path to a CSV file
Process -> auto-detect a date/numeric/category column and build three plotly charts;
           with --explain, send a small profile of the data to the AI for a summary
Output  -> a local web app at http://127.0.0.1:8050 (open it in your browser)

Run it like:
    uv run demos/02-data-to-dashboard/dashboard.py SALES.csv
    uv run demos/02-data-to-dashboard/dashboard.py SALES.csv --explain

Needs: nothing for the charts. --explain needs OPENAI_API_KEY in the repo-root .env.
Press Ctrl+C to stop the server. Read-only: it never modifies your CSV.
"""

import argparse
import os
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

REPO_ROOT = Path(__file__).resolve().parents[2]


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


def profile_data(df: pd.DataFrame) -> str:
    """A compact, text-only snapshot of the data — cheap to send, safe to read."""
    lines = [f"Rows: {len(df)}, Columns: {list(df.columns)}"]
    described = df.describe(include="all").round(2)
    lines.append("Summary statistics:\n" + described.to_string())
    return "\n".join(lines)


def explain_data(df: pd.DataFrame) -> str:
    """Ask the AI to read the profile (never the raw rows) and flag what's notable."""
    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv(REPO_ROOT / ".env")
    if not os.environ.get("OPENAI_API_KEY"):
        print("No OPENAI_API_KEY found — skipping --explain.")
        print(f"Add OPENAI_API_KEY=your-key to {REPO_ROOT / '.env'} to enable it.")
        return ""

    prompt = ("You are a data analyst. Here is a profile of a dataset. In 4-5 short "
              "bullets, plain English, point out the notable patterns, outliers, or "
              "things worth a second look. Do not invent numbers you cannot see.\n\n"
              + profile_data(df))
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-5.6-luna",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def build_app(df: pd.DataFrame, title: str, explanation: str) -> Dash:
    app = Dash(__name__)
    card_style = {"background": "white", "padding": "16px",
                  "border": "2px solid black", "borderRadius": "4px"}
    children = [html.H1(title, style={"borderBottom": "2px solid black",
                                      "paddingBottom": "6px"})]
    # The AI's read sits ABOVE the charts — a lead to verify against the data below.
    if explanation:
        children.append(html.Div(
            style={**card_style, "marginBottom": "20px", "borderColor": "#1f6f3d"},
            children=[html.H3("What the AI noticed (verify against the charts)"),
                      dcc.Markdown(explanation)]))
    children.append(html.Div(
        style={"display": "grid", "gridTemplateColumns": "1fr 1fr",
               "gap": "20px", "alignItems": "start"},
        children=[html.Div(style=card_style,
                           children=[html.H3(name), dcc.Graph(figure=fig)])
                  for name, fig in build_figures(df)]))
    app.layout = html.Div(
        style={"backgroundColor": "#F5F5F5", "minHeight": "100vh",
               "fontFamily": "Helvetica", "padding": "20px"},
        children=children)
    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve an interactive dashboard for a CSV file.")
    parser.add_argument("csv_path", help="Path to the CSV file, e.g. SALES.csv")
    parser.add_argument("--explain", action="store_true",
                        help="Add an AI-written summary of notable patterns (needs OPENAI_API_KEY)")
    parser.add_argument("--port", type=int, default=8050,
                        help="Port for the local web server (default: 8050)")
    args = parser.parse_args()

    try:
        df = load_data(args.csv_path)
    except FileNotFoundError:
        print(f"CSV file not found: {args.csv_path}")
        raise SystemExit(1)

    print(f"Loaded {len(df)} rows, {len(df.columns)} columns.")
    explanation = ""
    if args.explain:
        print("Asking the AI to read the data...\n")
        explanation = explain_data(df)
        if explanation:
            print(explanation + "\n")

    print(f"Open http://127.0.0.1:{args.port} in your browser. Ctrl+C stops the server.")
    app = build_app(df, f"Dashboard — {args.csv_path}", explanation)
    app.run(debug=False, port=args.port)


if __name__ == "__main__":
    main()
