#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["flask"]
# ///

from __future__ import annotations
from flask import Flask, request, render_template_string, send_file, redirect, url_for
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Dict, List, Set
import io

app = Flask(__name__)

# -----------------------------------------------------
# Data Models
# -----------------------------------------------------

@dataclass
class Employee:
    name: str
    role: str
    work_days: Set[int]
    start_time: time
    end_time: time

@dataclass
class RosterEntry:
    date: date
    employee_name: str
    role: str
    start_time: time
    end_time: time

employees: Dict[str, Employee] = {}
vacations: Dict[str, Set[date]] = {}
staffing: Dict[int, Dict[str, int]] = {}
roster: List[RosterEntry] = []

WEEK = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]


# -----------------------------------------------------
# Helpers
# -----------------------------------------------------

def parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()

def parse_time(s: str) -> time:
    return datetime.strptime(s, "%H:%M").time()

def parse_days(s: str) -> Set[int]:
    toks = [x.strip().capitalize()[:3] for x in s.replace(",", " ").split()]
    return {WEEK.index(t) for t in toks if t in WEEK}


# -----------------------------------------------------
# HTML Template
# -----------------------------------------------------

BASE = """
<!DOCTYPE html>
<html>
<head>
    <title>Rostering App</title>
    <style>
        body { font-family: sans-serif; margin: 40px; background:#fafafa; }
        h2 { margin-top: 40px; }
        input, select { padding: 6px; margin: 4px; }
        .card { background:white; padding:20px; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.1); margin-bottom:20px; }
        .btn { background:#007bff; padding:8px 14px; color:white; border-radius:6px; text-decoration:none; }
        table { border-collapse:collapse; width:100%; margin-top:10px; }
        th, td { border:1px solid #ddd; padding:8px; text-align:left; }
    </style>
</head>
<body>
<h1>Office Rostering App</h1>

<div class="card">
    <h2>Add Employee</h2>
    <form method="post" action="/add_employee">
        <input name="name" placeholder="Name" required>
        <input name="role" placeholder="Role" required>
        <input name="days" placeholder="Work days (Mon-Fri)">
        <input name="start" placeholder="Start (09:00)">
        <input name="end" placeholder="End (17:00)">
        <button class="btn">Add</button>
    </form>
</div>

<div class="card">
    <h2>Add Vacation</h2>
    <form method="post" action="/add_vacation">
        <select name="name">
            {% for e in employees %}
            <option>{{e}}</option>
            {% endfor %}
        </select>
        <input name="start" type="date" required>
        <input name="end" type="date" required>
        <button class="btn">Add</button>
    </form>
</div>

<div class="card">
    <h2>Staffing Requirements</h2>
    <form method="post" action="/set_staffing">
        <select name="weekday">
            {% for i, w in week_list %}
            <option value="{{i}}">{{w}}</option>
            {% endfor %}
        </select>
        <input name="role" placeholder="Role">
        <input name="min_staff" type="number" min="0" placeholder="Min staff">
        <button class="btn">Set</button>
    </form>

    <h3>Current Requirements</h3>
    <ul>
    {% for d, roles in staffing.items() %}
        <li><b>{{week[d]}}</b>:
            {% for r, c in roles.items() %}
            {{r}}={{c}}
            {% endfor %}
        </li>
    {% endfor %}
    </ul>
</div>

<div class="card">
    <h2>Generate Roster</h2>
    <form method="post" action="/generate">
        <input name="start" type="date" required>
        <input name="end" type="date" required>
        <button class="btn">Generate</button>
    </form>
</div>

{% if roster %}
<div class="card">
    <h2>Roster</h2>
    <table>
        <tr><th>Date</th><th>Day</th><th>Employee</th><th>Role</th><th>Hours</th></tr>
        {% for r in roster %}
        <tr>
            <td>{{r.date}}</td>
            <td>{{week[r.date.weekday()]}}</td>
            <td>{{r.employee_name}}</td>
            <td>{{r.role}}</td>
            <td>{{r.start_time}}-{{r.end_time}}</td>
        </tr>
        {% endfor %}
    </table>

    <p>
        <a class="btn" href="/export_csv">Export CSV</a>
        <a class="btn" href="/export_ics">Export ICS</a>
    </p>
</div>
{% endif %}

</body>
</html>
"""


# -----------------------------------------------------
# Routes
# -----------------------------------------------------

@app.route("/")
def index():
    week_list = list(enumerate(WEEK))  # [(0,"Mon"), (1,"Tue"), ...]
    return render_template_string(
        BASE, 
        employees=list(employees.keys()), 
        staffing=staffing,
        week=WEEK,
        week_list=week_list,
        roster=roster
    )

@app.route("/add_employee", methods=["POST"])
def add_employee():
    name = request.form["name"]
    role = request.form["role"]
    days = parse_days(request.form["days"]) if request.form["days"] else set(range(5))
    start = parse_time(request.form["start"] or "09:00")
    end = parse_time(request.form["end"] or "17:00")
    employees[name] = Employee(name, role, days, start, end)
    return redirect(url_for("index"))

@app.route("/add_vacation", methods=["POST"])
def add_vacation():
    name = request.form["name"]
    start = parse_date(request.form["start"])
    end = parse_date(request.form["end"])
    vac = vacations.setdefault(name, set())
    cur = start
    while cur <= end:
        vac.add(cur)
        cur += timedelta(days=1)
    return redirect(url_for("index"))

@app.route("/set_staffing", methods=["POST"])
def set_staffing():
    wd = int(request.form["weekday"])
    role = request.form["role"]
    if not role:
        return redirect(url_for("index"))
    c = int(request.form["min_staff"])
    staffing.setdefault(wd, {})[role] = c
    return redirect(url_for("index"))

@app.route("/generate", methods=["POST"])
def generate():
    global roster
    roster = []

    start = parse_date(request.form["start"])
    end = parse_date(request.form["end"])

    last_index: Dict[str, int] = {}

    cur = start
    while cur <= end:
        wd = cur.weekday()
        day_require = staffing.get(wd, {})

        for role, needed in day_require.items():
            cands = [
                e for e in employees.values()
                if e.role == role
                and wd in e.work_days
                and cur not in vacations.get(e.name, set())
            ]
            cands.sort(key=lambda e: e.name)

            if not cands:
                continue

            assign = min(len(cands), needed)
            li = last_index.get(role, -1)

            for i in range(assign):
                idx = (li + 1 + i) % len(cands)
                emp = cands[idx]
                roster.append(RosterEntry(cur, emp.name, emp.role, emp.start_time, emp.end_time))

            last_index[role] = (li + assign) % len(cands)

        cur += timedelta(days=1)

    return redirect(url_for("index"))


# -----------------------------------------------------
# Export
# -----------------------------------------------------

@app.route("/export_csv")
def export_csv():
    if not roster:
        return redirect(url_for("index"))
    buf = io.StringIO()
    buf.write("date,weekday,employee,role,start,end\n")
    for r in roster:
        buf.write(f"{r.date},{WEEK[r.date.weekday()]},{r.employee_name},{r.role},{r.start_time},{r.end_time}\n")
    buf.seek(0)
    return send_file(
        io.BytesIO(buf.getvalue().encode()),
        as_attachment=True,
        download_name="roster.csv",
        mimetype="text/csv"
    )

@app.route("/export_ics")
def export_ics():
    if not roster:
        return redirect(url_for("index"))

    def dtfmt(d, t): return datetime.combine(d, t).strftime("%Y%m%dT%H%M%S")

    lines = ["BEGIN:VCALENDAR","VERSION:2.0"]
    for i, r in enumerate(roster):
        lines += [
            "BEGIN:VEVENT",
            f"UID:{i}@rostering",
            f"DTSTART:{dtfmt(r.date, r.start_time)}",
            f"DTEND:{dtfmt(r.date, r.end_time)}",
            f"SUMMARY:{r.role}: {r.employee_name}",
            "END:VEVENT"
        ]
    lines.append("END:VCALENDAR")

    data = "\n".join(lines).encode()
    return send_file(
        io.BytesIO(data),
        as_attachment=True,
        download_name="roster.ics",
        mimetype="text/calendar"
    )


# -----------------------------------------------------
# Run
# -----------------------------------------------------

if __name__ == "__main__":
    print("Rostering app running at http://127.0.0.1:5000")
    app.run(debug=False)
