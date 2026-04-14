#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Simple Office Rostering App (CLI)

Features:
- Add employees (name, role, usual working days, working hours)
- Add vacation/leave dates per employee
- Define minimum staffing levels per role and weekday
- Automatically generate a roster for a given date range:
    * Respects employee working days/hours
    * Skips employees on vacation
    * Tries to meet minimum staffing per role/day (warns if impossible)
- Export roster to:
    * CSV: roster.csv
    * ICS calendar: roster.ics
- View roster as a table in the terminal
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Dict, List, Set


# ---------- Data Models ----------

@dataclass
class Employee:
    name: str
    role: str
    work_days: Set[int]  # 0=Monday ... 6=Sunday
    start_time: time
    end_time: time


@dataclass
class RosterEntry:
    date: date
    employee_name: str
    role: str
    start_time: time
    end_time: time


# ---------- Global In-Memory "DB" ----------

employees: Dict[str, Employee] = {}
vacations: Dict[str, Set[date]] = {}
staffing_requirements: Dict[int, Dict[str, int]] = {}  # weekday -> {role: min_staff}
roster: List[RosterEntry] = []


# ---------- Helpers ----------

WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def parse_weekdays(s: str) -> Set[int]:
    """
    Parse a string like "Mon,Tue,Fri" or "mon fri" into a set of weekday ints.
    """
    s = s.replace(",", " ")
    tokens = [t.strip().capitalize()[:3] for t in s.split() if t.strip()]
    result: Set[int] = set()
    for tok in tokens:
        if tok in WEEKDAY_NAMES:
            result.add(WEEKDAY_NAMES.index(tok))
        else:
            print(f"Unknown weekday token: {tok} (ignored)")
    return result


def parse_time_str(s: str) -> time:
    """
    Parse HH:MM into datetime.time.
    """
    try:
        hour, minute = s.split(":")
        return time(hour=int(hour), minute=int(minute))
    except Exception:
        raise ValueError(f"Invalid time format: {s}. Use HH:MM, e.g. 09:00")


def parse_date_str(s: str) -> date:
    """
    Parse YYYY-MM-DD into datetime.date.
    """
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        raise ValueError(f"Invalid date format: {s}. Use YYYY-MM-DD")


def input_nonempty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Value cannot be empty.")


def print_header(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


# ---------- Employee Management ----------

def add_employee() -> None:
    print_header("Add Employee")
    name = input_nonempty("Employee name: ")
    if name in employees:
        print("Employee with this name already exists. Overwriting info.")

    role = input_nonempty("Role (e.g. Reception, Manager, Support): ")

    print("Enter normal working days (e.g. Mon-Fri or Mon,Wed,Fri):")
    work_days_str = input_nonempty("Working days: ")
    work_days = parse_weekdays(work_days_str)
    if not work_days:
        print("No valid working days parsed. Defaulting to Mon-Fri.")
        work_days = set(range(5))

    start_time = parse_time_str(input_nonempty("Start time (HH:MM, e.g. 09:00): "))
    end_time = parse_time_str(input_nonempty("End time (HH:MM, e.g. 17:00): "))

    employees[name] = Employee(
        name=name,
        role=role,
        work_days=work_days,
        start_time=start_time,
        end_time=end_time,
    )
    print(f"Employee '{name}' added/updated.")


def list_employees() -> None:
    print_header("Employees")
    if not employees:
        print("No employees defined yet.")
        return
    print(f"{'Name':20} {'Role':15} {'Days':20} {'Hours':10}")
    print("-" * 70)
    for e in employees.values():
        days = ",".join(WEEKDAY_NAMES[d] for d in sorted(e.work_days))
        hours = f"{e.start_time.strftime('%H:%M')}-{e.end_time.strftime('%H:%M')}"
        print(f"{e.name:20} {e.role:15} {days:20} {hours:10}")


# ---------- Vacation Management ----------

def add_vacation() -> None:
    print_header("Add Vacation / Leave")
    if not employees:
        print("No employees to assign vacation to. Add employees first.")
        return

    name = input_nonempty("Employee name (must exist): ")
    if name not in employees:
        print(f"Employee '{name}' not found.")
        return

    start_str = input_nonempty("Vacation start date (YYYY-MM-DD): ")
    end_str = input_nonempty("Vacation end date (YYYY-MM-DD): ")
    start = parse_date_str(start_str)
    end = parse_date_str(end_str)
    if end < start:
        print("End date is before start date. Swapping.")
        start, end = end, start

    days = vacations.setdefault(name, set())
    cur = start
    while cur <= end:
        days.add(cur)
        cur += timedelta(days=1)

    print(
        f"Vacation recorded for {name} from {start.isoformat()} to {end.isoformat()} "
        f"({(end - start).days + 1} day(s))."
    )


def list_vacations() -> None:
    print_header("Vacations / Leave")
    if not vacations:
        print("No vacations recorded yet.")
        return

    for name, days in vacations.items():
        sorted_days = sorted(days)
        print(f"\n{name}:")
        for d in sorted_days:
            print(f"  - {d.isoformat()} ({WEEKDAY_NAMES[d.weekday()]})")


# ---------- Staffing Requirements ----------

def set_staffing_requirements() -> None:
    print_header("Set Staffing Requirements by Weekday and Role")
    print("You can configure minimum staff per role for each weekday.")
    print("Leave role blank to move to next weekday.")
    print("Example: Role=Reception, Min staff=2")

    for wd in range(7):
        print(f"\n--- {WEEKDAY_NAMES[wd]} ---")
        role_map: Dict[str, int] = staffing_requirements.get(wd, {})
        while True:
            role = input("Role (blank to finish this day): ").strip()
            if not role:
                break
            min_str = input_nonempty(f"Minimum staff for role '{role}' on {WEEKDAY_NAMES[wd]}: ")
            try:
                min_staff = int(min_str)
                if min_staff < 0:
                    raise ValueError
            except ValueError:
                print("Please enter a non-negative integer.")
                continue
            role_map[role] = min_staff
            print(f"Set {WEEKDAY_NAMES[wd]} / {role} -> {min_staff}")
        if role_map:
            staffing_requirements[wd] = role_map

    print("\nStaffing requirements updated.")


def show_staffing_requirements() -> None:
    print_header("Current Staffing Requirements")
    if not staffing_requirements:
        print("No staffing requirements defined.")
        return
    for wd in range(7):
        if wd not in staffing_requirements:
            continue
        print(f"\n{WEEKDAY_NAMES[wd]}:")
        for role, min_staff in staffing_requirements[wd].items():
            print(f"  - {role}: {min_staff} staff")


# ---------- Roster Generation ----------

def generate_roster() -> None:
    global roster
    print_header("Generate Roster")
    if not employees:
        print("No employees defined. Add employees first.")
        return
    if not staffing_requirements:
        print("No staffing requirements defined. Set them first.")
        return

    start_str = input_nonempty("Roster start date (YYYY-MM-DD): ")
    end_str = input_nonempty("Roster end date (YYYY-MM-DD): ")
    start = parse_date_str(start_str)
    end = parse_date_str(end_str)
    if end < start:
        print("End date is before start date. Swapping.")
        start, end = end, start

    roster = []
    per_role_last_index: Dict[str, int] = {}

    cur = start
    while cur <= end:
        wd = cur.weekday()
        day_requirements = staffing_requirements.get(wd, {})
        if not day_requirements:
            cur += timedelta(days=1)
            continue

        for role, min_staff in day_requirements.items():
            if min_staff <= 0:
                continue

            candidates = [
                e
                for e in employees.values()
                if e.role == role
                and wd in e.work_days
                and cur not in vacations.get(e.name, set())
            ]
            candidates.sort(key=lambda e: e.name)

            if not candidates:
                print(
                    f"WARNING: {cur.isoformat()} ({WEEKDAY_NAMES[wd]}): "
                    f"No available employees for role '{role}'."
                )
                continue

            if len(candidates) < min_staff:
                print(
                    f"WARNING: {cur.isoformat()} ({WEEKDAY_NAMES[wd]}): "
                    f"Needed {min_staff} for role '{role}', only {len(candidates)} available. "
                    f"Assigning all available."
                )

            # Round-robin assignment
            count_to_assign = min(min_staff, len(candidates))
            last_idx = per_role_last_index.get(role, -1)
            for i in range(count_to_assign):
                idx = (last_idx + 1 + i) % len(candidates)
                emp = candidates[idx]
                roster.append(
                    RosterEntry(
                        date=cur,
                        employee_name=emp.name,
                        role=emp.role,
                        start_time=emp.start_time,
                        end_time=emp.end_time,
                    )
                )
            per_role_last_index[role] = (last_idx + count_to_assign) % len(candidates)

        cur += timedelta(days=1)

    print(f"\nRoster generated with {len(roster)} entries.")


def view_roster() -> None:
    print_header("Roster (Table View)")
    if not roster:
        print("No roster generated yet.")
        return
    print(f"{'Date':12} {'Day':4} {'Employee':20} {'Role':15} {'Hours':10}")
    print("-" * 70)
    for entry in sorted(roster, key=lambda r: (r.date, r.role, r.employee_name)):
        date_str = entry.date.isoformat()
        day_str = WEEKDAY_NAMES[entry.date.weekday()]
        hours = f"{entry.start_time.strftime('%H:%M')}-{entry.end_time.strftime('%H:%M')}"
        print(f"{date_str:12} {day_str:4} {entry.employee_name:20} {entry.role:15} {hours:10}")


# ---------- Export Functions ----------

def export_roster_csv(filename: str = "roster.csv") -> None:
    if not roster:
        print("No roster to export. Generate it first.")
        return
    lines = ["date,weekday,employee,role,start_time,end_time"]
    for entry in sorted(roster, key=lambda r: (r.date, r.role, r.employee_name)):
        lines.append(
            ",".join(
                [
                    entry.date.isoformat(),
                    WEEKDAY_NAMES[entry.date.weekday()],
                    entry.employee_name.replace(",", " "),
                    entry.role.replace(",", " "),
                    entry.start_time.strftime("%H:%M"),
                    entry.end_time.strftime("%H:%M"),
                ]
            )
        )
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Roster exported to {filename}")


def export_roster_ics(filename: str = "roster.ics") -> None:
    if not roster:
        print("No roster to export. Generate it first.")
        return

    def dtstamp() -> str:
        return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    def dt_local(d: date, t: time) -> str:
        # Naive local datetime in "floating time" (no timezone)
        return datetime.combine(d, t).strftime("%Y%m%dT%H%M%S")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//OfficeRoster//EN",
    ]

    now_stamp = dtstamp()
    for idx, entry in enumerate(roster, start=1):
        uid = f"{idx}-{entry.date.isoformat()}-{entry.employee_name.replace(' ', '')}@office-roster"
        start_dt = dt_local(entry.date, entry.start_time)
        end_dt = dt_local(entry.date, entry.end_time)
        summary = f"{entry.role}: {entry.employee_name}"
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{now_stamp}",
                f"DTSTART:{start_dt}",
                f"DTEND:{end_dt}",
                f"SUMMARY:{summary}",
                "END:VEVENT",
            ]
        )

    lines.append("END:VCALENDAR")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Roster exported to {filename} (ICS calendar)")


# ---------- Main Menu ----------

def main_menu() -> None:
    while True:
        print_header("Office Rostering App")
        print("1) Add employee")
        print("2) List employees")
        print("3) Add vacation/leave")
        print("4) List vacations/leave")
        print("5) Set staffing requirements")
        print("6) Show staffing requirements")
        print("7) Generate roster")
        print("8) View roster (table)")
        print("9) Export roster to CSV")
        print("10) Export roster to ICS calendar")
        print("0) Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_employee()
        elif choice == "2":
            list_employees()
        elif choice == "3":
            add_vacation()
        elif choice == "4":
            list_vacations()
        elif choice == "5":
            set_staffing_requirements()
        elif choice == "6":
            show_staffing_requirements()
        elif choice == "7":
            generate_roster()
        elif choice == "8":
            view_roster()
        elif choice == "9":
            export_roster_csv()
        elif choice == "10":
            export_roster_ics()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main_menu()
