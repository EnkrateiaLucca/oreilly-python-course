# /// script
# requires-python = ">=3.12"
# ///
"""A tiny time-tracker you drive from the terminal: start, stop, report.

The pattern behind tools like `git` and `docker`: ONE command with several
SUB-commands. The "database" is just a JSON file in your home folder.

Run it like:
    uv run demos/reserve/track.py start "Writing the report"
    uv run demos/reserve/track.py status
    uv run demos/reserve/track.py stop
    uv run demos/reserve/track.py report

Your log lives in ~/.track_log.json so it survives between runs.
Needs: nothing (no API key, standard library only).
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path.home() / ".track_log.json"


def load_log() -> list:
    """Read the list of past sessions, or start empty if the file is new."""
    if LOG_FILE.exists():
        return json.loads(LOG_FILE.read_text())
    return []


def save_log(log: list) -> None:
    LOG_FILE.write_text(json.dumps(log, indent=2))


def format_duration(seconds: float) -> str:
    """Turn seconds into a friendly '1h 23m' string."""
    minutes = int(seconds // 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes:02d}m"


def cmd_start(task: str) -> None:
    log = load_log()
    # Never let two timers run at once: close any open session first.
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
        print('Nothing is running. Start something with: track start "my task"')
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

    totals: dict[str, float] = {}
    for session in log:
        if session.get("end") is None:
            continue  # skip a session that is still running
        seconds = (datetime.fromisoformat(session["end"])
                   - datetime.fromisoformat(session["start"])).total_seconds()
        totals[session["task"]] = totals.get(session["task"], 0) + seconds

    print("Time by task")
    print("-" * 32)
    for task, seconds in sorted(totals.items(), key=lambda item: item[1], reverse=True):
        print(f"{format_duration(seconds):>8}  {task}")
    print("-" * 32)
    print(f"{format_duration(sum(totals.values())):>8}  TOTAL")


def main() -> None:
    parser = argparse.ArgumentParser(description="A tiny terminal time-tracker.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start", help="Start timing a task.")
    start_parser.add_argument("task", help='What you are working on, e.g. "Writing the report".')
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


if __name__ == "__main__":
    main()
