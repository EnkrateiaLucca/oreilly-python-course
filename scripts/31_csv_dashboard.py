#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pandas",
#   "plotly",
#   "dash",
# ]
# ///
"""
Automata Learning Lab - Minimal Dashboard (Final Fixed Version)
"""

import argparse
import pandas as pd
from dash import Dash, dcc, html
import plotly.express as px


# ------------------------------------------------------------
# SAFE DATE PARSER (no errors='ignore', no warnings)
# ------------------------------------------------------------
def safe_parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if "date" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass
    return df


# ------------------------------------------------------------
# LOAD CSV
# ------------------------------------------------------------
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = safe_parse_dates(df)
    return df


# ------------------------------------------------------------
# PLOT STYLE
# ------------------------------------------------------------
def style(fig):
    fig.update_layout(
        template="simple_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Helvetica", color="#000000"),
        margin=dict(l=40, r=20, t=50, b=40),
    )
    return fig


# ------------------------------------------------------------
# BUILD DASH APP
# ------------------------------------------------------------
def build_app(df: pd.DataFrame) -> Dash:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    cat_col = next((c for c in df.columns if df[c].dtype == "object"), None)
    date_col = next((c for c in df.columns if "date" in c.lower()), None)

    figures = []

    # 1. Time series
    if date_col and numeric_cols:
        fig_ts = px.line(
            df.sort_values(date_col),
            x=date_col,
            y=numeric_cols[0],
            title=f"{numeric_cols[0]} Over Time",
        )
        figures.append(("Time Series", style(fig_ts)))

    # 2. Distribution
    if numeric_cols:
        fig_hist = px.histogram(
            df, x=numeric_cols[0], title=f"Distribution of {numeric_cols[0]}"
        )
        figures.append(("Distribution", style(fig_hist)))

    # 3. Category Breakdown
    if cat_col and numeric_cols:
        grouped = (
            df.groupby(cat_col)[numeric_cols[0]]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
        )
        fig_bar = px.bar(
            grouped, x=cat_col, y=numeric_cols[0], title=f"{numeric_cols[0]} by {cat_col}"
        )
        figures.append(("Category Breakdown", style(fig_bar)))

    # ---- Layout ----
    app = Dash(__name__)

    app.layout = html.Div(
        style={
            "backgroundColor": "#F5F5F5",
            "minHeight": "100vh",
            "fontFamily": "Helvetica",
            "padding": "20px",
        },
        children=[
            html.H1(
                "Automata Learning Lab — Dashboard",
                style={"borderBottom": "2px solid black", "paddingBottom": "6px"},
            ),
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "1fr 1fr",
                    "gap": "20px",
                    "alignItems": "start",  # FIX
                },
                children=[
                    html.Div(
                        style={
                            "background": "white",
                            "padding": "16px",
                            "border": "2px solid black",
                            "borderRadius": "4px",
                            "height": "420px",        # KEY FIX
                            "overflow": "hidden",      # KEY FIX
                            "display": "flex",
                            "flexDirection": "column",
                        },
                        children=[
                            html.H3(title, style={"marginBottom": "10px"}),
                            dcc.Graph(
                                figure=fig,
                                style={
                                    "flex": "1",
                                    "height": "320px",  # FIXED GRAPH HEIGHT
                                },
                            ),
                        ],
                    )
                    for title, fig in figures
                ],
            ),
        ],
    )

    return app


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", help="Path to CSV file")
    args = parser.parse_args()

    df = load_data(args.csv_path)
    app = build_app(df)

    app.run(debug=False)


if __name__ == "__main__":
    main()