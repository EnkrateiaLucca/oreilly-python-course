#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pandas>=2.0"]
# ///
"""
Sales dashboard generator.

Reads a sales CSV with the columns:
    Region, Country, Item Type, Sales Channel, Order Priority,
    Order Date, Order ID, Ship Date, Units Sold, Unit Price,
    Unit Cost, Total Revenue, Total Cost, Total Profit

and writes a single self-contained interactive HTML dashboard.

Usage:
    uv run sales_dashboard.py SALES.csv [-o dashboard.html]
    uv run sales_dashboard.py SALES.csv --open
"""

from __future__ import annotations

import argparse
import json
import sys
import webbrowser
from pathlib import Path

import pandas as pd

EXPECTED_COLUMNS = [
    "Region", "Country", "Item Type", "Sales Channel", "Order Priority",
    "Order Date", "Order ID", "Ship Date", "Units Sold", "Unit Price",
    "Unit Cost", "Total Revenue", "Total Cost", "Total Profit",
]


def load_data(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]

    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        sys.exit(f"Error: CSV is missing expected columns: {missing}")

    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce")
    for col in ["Units Sold", "Unit Price", "Unit Cost",
                "Total Revenue", "Total Cost", "Total Profit"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Order Date"])
    df["Year"] = df["Order Date"].dt.year
    df["YearMonth"] = df["Order Date"].dt.strftime("%Y-%m")
    return df


def build_records(df: pd.DataFrame) -> list[dict]:
    out = df.copy()
    out["Order Date"] = out["Order Date"].dt.strftime("%Y-%m-%d")
    out["Ship Date"] = out["Ship Date"].dt.strftime("%Y-%m-%d")
    keep = EXPECTED_COLUMNS + ["Year", "YearMonth"]
    return out[keep].to_dict(orient="records")


def render_html(records: list[dict], source_name: str) -> str:
    data_json = json.dumps(records, default=str)
    return _HTML_TEMPLATE.replace("__DATA__", data_json).replace(
        "__SOURCE__", json.dumps(source_name)
    )


_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sales Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root{
    --bg:#0f1419; --panel:#1a212b; --panel-2:#222c38; --line:#2c3744;
    --text:#e7edf3; --muted:#8a99a8; --accent:#4cc9f0; --accent-2:#f72585;
    --good:#52c41a; --warn:#faad14;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--text);
    font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
  header{padding:22px 28px;border-bottom:1px solid var(--line);
    display:flex;align-items:baseline;gap:14px;flex-wrap:wrap}
  header h1{font-size:20px;margin:0;font-weight:650;letter-spacing:.2px}
  header .src{color:var(--muted);font-size:13px}
  .wrap{padding:22px 28px;max-width:1400px;margin:0 auto}
  .filters{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:22px}
  .filters label{display:flex;flex-direction:column;font-size:11px;
    color:var(--muted);gap:5px;text-transform:uppercase;letter-spacing:.6px}
  select{background:var(--panel-2);color:var(--text);border:1px solid var(--line);
    border-radius:8px;padding:8px 10px;font-size:13px;min-width:150px}
  .kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
    gap:14px;margin-bottom:22px}
  .kpi{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px}
  .kpi .v{font-size:24px;font-weight:700;margin-top:6px}
  .kpi .l{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.6px}
  .grid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}
  @media(max-width:900px){.grid{grid-template-columns:1fr}}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px}
  .card.full{grid-column:1/-1}
  .card .head{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
  .card h3{margin:0;font-size:14px;font-weight:600}
  .card .canvas-wrap{position:relative;height:300px}
  button.exp{background:var(--accent);color:#06222d;border:none;border-radius:7px;
    padding:6px 11px;font-size:12px;font-weight:600;cursor:pointer}
  button.exp:hover{opacity:.9}
  table{width:100%;border-collapse:collapse;font-size:13px}
  th,td{padding:7px 9px;text-align:left;border-bottom:1px solid var(--line)}
  th{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.5px;
    cursor:pointer;user-select:none}
  td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
  .tbl-wrap{max-height:340px;overflow:auto}
</style>
</head>
<body>
<header>
  <h1>Sales Dashboard</h1>
  <span class="src">Source: <span id="srcName"></span></span>
</header>

<div class="wrap">
  <div class="filters" id="filters">
    <label>Region<select id="fRegion"></select></label>
    <label>Country<select id="fCountry"></select></label>
    <label>Item Type<select id="fItem"></select></label>
    <label>Channel<select id="fChannel"></select></label>
    <label>Priority<select id="fPriority"></select></label>
    <label>Year<select id="fYear"></select></label>
  </div>

  <div class="kpis" id="kpis"></div>

  <div class="grid">
    <div class="card">
      <div class="head"><h3>Revenue over time</h3>
        <button class="exp" data-chart="ts">Export PNG</button></div>
      <div class="canvas-wrap"><canvas id="cTs"></canvas></div>
    </div>
    <div class="card">
      <div class="head"><h3>Profit by region</h3>
        <button class="exp" data-chart="region">Export PNG</button></div>
      <div class="canvas-wrap"><canvas id="cRegion"></canvas></div>
    </div>
    <div class="card">
      <div class="head"><h3>Revenue by item type</h3>
        <button class="exp" data-chart="item">Export PNG</button></div>
      <div class="canvas-wrap"><canvas id="cItem"></canvas></div>
    </div>
    <div class="card">
      <div class="head"><h3>Sales channel split</h3>
        <button class="exp" data-chart="channel">Export PNG</button></div>
      <div class="canvas-wrap"><canvas id="cChannel"></canvas></div>
    </div>
    <div class="card full">
      <div class="head"><h3>Top countries by profit</h3>
        <button class="exp" data-chart="country">Export PNG</button></div>
      <div class="canvas-wrap" style="height:340px"><canvas id="cCountry"></canvas></div>
    </div>
    <div class="card full">
      <div class="head"><h3>Detail (filtered, top 200 by revenue)</h3>
        <button class="exp" data-csv="1">Export CSV</button></div>
      <div class="tbl-wrap"><table id="tbl"><thead></thead><tbody></tbody></table></div>
    </div>
  </div>
</div>

<script>
const RAW = __DATA__;
const SRC = __SOURCE__;
document.getElementById("srcName").textContent = SRC;

const fmt = n => n>=1e9?(n/1e9).toFixed(2)+"B":n>=1e6?(n/1e6).toFixed(2)+"M":
  n>=1e3?(n/1e3).toFixed(1)+"K":(Math.round(n*100)/100).toLocaleString();
const money = n => "$"+fmt(n);

const FILTERS = {
  fRegion:"Region", fCountry:"Country", fItem:"Item Type",
  fChannel:"Sales Channel", fPriority:"Order Priority", fYear:"Year"
};
function uniq(key){return [...new Set(RAW.map(r=>r[key]))].sort();}
for(const [id,key] of Object.entries(FILTERS)){
  const sel=document.getElementById(id);
  sel.innerHTML='<option value="">All</option>'+
    uniq(key).map(v=>`<option>${v}</option>`).join("");
  sel.addEventListener("change",refresh);
}

function applyFilters(){
  return RAW.filter(r=>{
    for(const [id,key] of Object.entries(FILTERS)){
      const v=document.getElementById(id).value;
      if(v!=="" && String(r[key])!==v) return false;
    }
    return true;
  });
}

function groupSum(rows,key,field){
  const m=new Map();
  for(const r of rows){m.set(r[key],(m.get(r[key])||0)+(+r[field]||0));}
  return [...m.entries()].sort((a,b)=>b[1]-a[1]);
}

const PALETTE=["#4cc9f0","#f72585","#7209b7","#3a0ca3","#4361ee",
  "#52c41a","#faad14","#fb8500","#06d6a0","#ef476f","#8338ec","#ffbe0b"];
const GRID="#2c3744", TICK="#8a99a8";
Chart.defaults.color=TICK; Chart.defaults.borderColor=GRID;
const charts={};

function mkChart(id,key,cfg){
  if(charts[key]) charts[key].destroy();
  charts[key]=new Chart(document.getElementById(id),cfg);
}

function refresh(){
  const rows=applyFilters();

  const rev=rows.reduce((s,r)=>s+(+r["Total Revenue"]||0),0);
  const prof=rows.reduce((s,r)=>s+(+r["Total Profit"]||0),0);
  const units=rows.reduce((s,r)=>s+(+r["Units Sold"]||0),0);
  const margin=rev?(prof/rev*100):0;
  document.getElementById("kpis").innerHTML=[
    ["Orders",rows.length.toLocaleString()],
    ["Total Revenue",money(rev)],
    ["Total Profit",money(prof)],
    ["Units Sold",fmt(units)],
    ["Profit Margin",margin.toFixed(1)+"%"],
  ].map(([l,v])=>`<div class="kpi"><div class="l">${l}</div><div class="v">${v}</div></div>`).join("");

  const ts=groupSum(rows,"YearMonth","Total Revenue").sort((a,b)=>a[0]<b[0]?-1:1);
  mkChart("cTs","ts",{type:"line",data:{labels:ts.map(d=>d[0]),
    datasets:[{label:"Revenue",data:ts.map(d=>d[1]),borderColor:PALETTE[0],
      backgroundColor:"rgba(76,201,240,.15)",fill:true,tension:.25,pointRadius:0}]},
    options:baseOpts(true)});

  const reg=groupSum(rows,"Region","Total Profit");
  mkChart("cRegion","region",{type:"bar",data:{labels:reg.map(d=>d[0]),
    datasets:[{label:"Profit",data:reg.map(d=>d[1]),backgroundColor:PALETTE[1]}]},
    options:baseOpts(true)});

  const item=groupSum(rows,"Item Type","Total Revenue");
  mkChart("cItem","item",{type:"bar",data:{labels:item.map(d=>d[0]),
    datasets:[{label:"Revenue",data:item.map(d=>d[1]),backgroundColor:PALETTE[3]}]},
    options:{...baseOpts(true),indexAxis:"y"}});

  const ch=groupSum(rows,"Sales Channel","Total Revenue");
  mkChart("cChannel","channel",{type:"doughnut",data:{labels:ch.map(d=>d[0]),
    datasets:[{data:ch.map(d=>d[1]),backgroundColor:PALETTE}]},
    options:{responsive:true,maintainAspectRatio:false,
      plugins:{legend:{position:"bottom"}}}});

  const ctry=groupSum(rows,"Country","Total Profit").slice(0,15);
  mkChart("cCountry","country",{type:"bar",data:{labels:ctry.map(d=>d[0]),
    datasets:[{label:"Profit",data:ctry.map(d=>d[1]),backgroundColor:PALETTE[5]}]},
    options:baseOpts(true)});

  renderTable(rows);
}

function baseOpts(hideLegend){
  return {responsive:true,maintainAspectRatio:false,
    plugins:{legend:{display:!hideLegend}},
    scales:{x:{grid:{color:GRID}},y:{grid:{color:GRID},
      ticks:{callback:v=>fmt(v)}}}};
}

let sortKey="Total Revenue", sortDir=-1;
const COLS=["Order Date","Region","Country","Item Type","Sales Channel",
  "Order Priority","Units Sold","Total Revenue","Total Profit"];
const NUMCOLS=new Set(["Units Sold","Total Revenue","Total Profit"]);
let lastRows=[];

function renderTable(rows){
  lastRows=rows;
  const sorted=[...rows].sort((a,b)=>{
    let x=a[sortKey],y=b[sortKey];
    if(NUMCOLS.has(sortKey)){x=+x;y=+y;}
    return x<y?sortDir:x>y?-sortDir:0;
  }).slice(0,200);
  document.querySelector("#tbl thead").innerHTML="<tr>"+COLS.map(c=>
    `<th class="${NUMCOLS.has(c)?'num':''}" data-c="${c}">${c}${sortKey===c?(sortDir<0?" ▼":" ▲"):""}</th>`).join("")+"</tr>";
  document.querySelector("#tbl tbody").innerHTML=sorted.map(r=>"<tr>"+COLS.map(c=>{
    let v=r[c]; if(NUMCOLS.has(c)) v=(c==="Units Sold")?(+v).toLocaleString():money(+v);
    return `<td class="${NUMCOLS.has(c)?'num':''}">${v}</td>`;}).join("")+"</tr>").join("");
  document.querySelectorAll("#tbl th").forEach(th=>th.onclick=()=>{
    const c=th.dataset.c; if(sortKey===c) sortDir*=-1; else {sortKey=c;sortDir=-1;}
    renderTable(lastRows);
  });
}

document.querySelectorAll("button.exp").forEach(btn=>btn.onclick=()=>{
  if(btn.dataset.csv){ exportCsv(); return; }
  const c=charts[btn.dataset.chart]; if(!c) return;
  const link=document.createElement("a");
  // paint solid background so the PNG isn't transparent
  const src=c.canvas, tmp=document.createElement("canvas");
  tmp.width=src.width; tmp.height=src.height;
  const ctx=tmp.getContext("2d");
  ctx.fillStyle="#1a212b"; ctx.fillRect(0,0,tmp.width,tmp.height);
  ctx.drawImage(src,0,0);
  link.download=btn.dataset.chart+"_chart.png";
  link.href=tmp.toDataURL("image/png"); link.click();
});

function exportCsv(){
  const head=COLS.join(",");
  const body=lastRows.map(r=>COLS.map(c=>{
    const v=String(r[c]??""); return /[",\n]/.test(v)?`"${v.replace(/"/g,'""')}"`:v;
  }).join(",")).join("\n");
  const blob=new Blob([head+"\n"+body],{type:"text/csv"});
  const link=document.createElement("a");
  link.download="filtered_sales.csv"; link.href=URL.createObjectURL(blob); link.click();
}

refresh();
</script>
</body>
</html>
"""


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate an interactive HTML sales dashboard from a CSV.")
    ap.add_argument("csv", type=Path, help="Path to the sales CSV file.")
    ap.add_argument("-o", "--output", type=Path, default=None,
                    help="Output HTML path (default: <csv stem>_dashboard.html).")
    ap.add_argument("--open", action="store_true", help="Open the dashboard in a browser when done.")
    args = ap.parse_args()

    if not args.csv.exists():
        sys.exit(f"Error: file not found: {args.csv}")

    df = load_data(args.csv)
    records = build_records(df)
    html = render_html(records, args.csv.name)

    out = args.output or args.csv.with_name(args.csv.stem + "_dashboard.html")
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out}  ({len(records):,} rows)")

    if args.open:
        webbrowser.open(out.resolve().as_uri())


if __name__ == "__main__":
    main()