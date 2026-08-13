# /// script
# requires-python = ">=3.10"
# ///
"""A tiny time-tracker you drive from the terminal: start, stop, report.

Automation category: CLI tools.

Input   -> sub-commands you type: start "task name", stop, status, report
Process -> append each event to a small JSON file with a timestamp
Output  -> a running log of what you worked on and for how long

This demo teaches the pattern behind tools like `git` and `docker`: ONE command
(`track`) with several SUB-commands (`start`, `stop`, ...). It also shows the
simplest possible database -- a JSON file on disk -- and how to do date math with
`datetime`. Real, useful, and only standard library.

Run it like:
    uv run scripts/demos/cli-tools/track.py start "Writing the report"
    uv run scripts/demos/cli-tools/track.py status
    uv run scripts/demos/cli-tools/track.py stop
    uv run scripts/demos/cli-tools/track.py report

Your log is saved to ~/.track_log.json so it survives between runs.

Needs: nothing (no API key).
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

# One JSON file in your home folder acts as our "database".
LOG_FILE = Path.home() / ".track_log.json"


def load_log() -> list:
    """Read the list of past sessions, or start empty if the file is new."""
    if LOG_FILE.exists():
        return json.loads(LOG_FILE.read_text())
    return []


def save_log(log: list) -> None:
    """Write the whole list back to disk as pretty JSON."""
    LOG_FILE.write_text(json.dumps(log, indent=2))


def format_duration(seconds: float) -> str:
    """Turn a number of seconds into a friendly '1h 23m' string."""
    minutes = int(seconds // 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes:02d}m"


def cmd_start(task: str) -> None:
    log = load_log()
    # If a session is still open (no 'end' yet), close it first so we never
    # have two timers running at once.
    if log and log[-1].get("end") is None:
        print("A session was already running -- stopping it first.")
        cmd_stop()
        log = load_log()

    log.append({"task": task, "start": datetime.now().isoformat(), "end": None})
    save_log(log)
    print(f"Started: {task}")


def cmd_stop() -> None:
    log = load_log()
    if not log or log[-1].get("end") is not None:
        print("Nothing is running. Start something with: track start \"my task\"")
        return

    session = log[-1]
    session["end"] = datetime.now().isoformat()
    save_log(log)

    elapsed = datetime.fromisoformat(session["end"]) - datetime.fromisoformat(session["start"])
    print(f"Stopped: {session['task']}  ({format_duration(elapsed.total_seconds())})")


def cmd_status() -> None:
    log = load_log()
    if log and log[-1].get("end") is None:
        session = log[-1]
        elapsed = datetime.now() - datetime.fromisoformat(session["start"])
        print(f"Running: {session['task']}  ({format_duration(elapsed.total_seconds())} so far)")
    else:
        print("No session running.")


def cmd_report() -> None:
    log = load_log()
    if not log:
        print("No sessions logged yet.")
        return

    # Add up total time per task name.
    totals: dict[str, float] = {}
    for session in log:
        if session.get("end") is None:
            continue  # skip a session that is still running
        seconds = (datetime.fromisoformat(session["end"]) - datetime.fromisoformat(session["start"])).total_seconds()
        totals[session["task"]] = totals.get(session["task"], 0) + seconds

    print("Time by task")
    print("-" * 32)
    for task, seconds in sorted(totals.items(), key=lambda item: item[1], reverse=True):
        print(f"{format_duration(seconds):>8}  {task}")
    print("-" * 32)
    print(f"{format_duration(sum(totals.values())):>8}  TOTAL")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A tiny terminal time-tracker.")
    # add_subparsers gives us 'track start', 'track stop', etc.
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start", help="Start timing a task.")
    start_parser.add_argument("task", help="What you're working on, e.g. \"Writing the report\".")

    subparsers.add_parser("stop", help="Stop the current task.")
    subparsers.add_parser("status", help="Show whether a task is running.")
    subparsers.add_parser("report", help="Show total time per task.")

    args = parser.parse_args()

    if args.command == "start":
        cmd_start(args.task)
    elif args.command == "stop":
        cmd_stop()
    elif args.command == "status":
        cmd_status()
    elif args.command == "report":
        cmd_report()
