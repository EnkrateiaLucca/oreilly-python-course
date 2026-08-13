# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
LESSON 09 — Capstone: the Downloads organizer, for real
=======================================================

This is the script the whole day has been building toward — and here's
the payoff: YOU CAN NOW READ EVERY LINE OF IT. Variables and f-strings
(01), lists and loops (02), the folder_for decision (03), pathlib (04),
the header and imports (05), argparse flags below — nothing here is new.

Safety design worth copying into every script AI writes for you:
  * It practices on its own sandbox folder (practice_downloads/,
    which it creates and fills itself) — NOT your real Downloads.
  * It's a DRY RUN by default: it only prints the plan.
  * Nothing moves until you add --apply. Nothing REAL is touched
    unless you also add --real and type YES at the prompt.

Run me (in this order!):
    uv run lessons/09_capstone_organizer.py                  # plan (sandbox)
    uv run lessons/09_capstone_organizer.py --apply          # move (sandbox)
    uv run lessons/09_capstone_organizer.py --real           # plan (Downloads)
    uv run lessons/09_capstone_organizer.py --real --apply   # the brave one
"""

# 🗣 EXPLAIN IT (before running): in one sentence — what is this script FOR?

import argparse
from pathlib import Path

# The practice sandbox lives right next to this script.
PRACTICE_FOLDER = Path(__file__).parent / "practice_downloads"

# The pretend mess from lesson 02 — now as actual files on disk.
SAMPLE_FILES = [
    "vacation.jpg", "screenshot.png", "team_photo.HEIC",
    "tax_return_2025.pdf", "invoice_march.pdf", "meeting_notes.txt",
    "song.mp3", "movie_clip.mov", "install_me.dmg",
    "sales_data.csv", "old_backup.zip", "mystery_download",
]


def folder_for(filename):
    """Lesson 03's decision function — the brain, unchanged."""
    name = filename.lower()
    if name.endswith((".jpg", ".jpeg", ".png", ".heic", ".gif")):
        return "Images"
    elif name.endswith((".pdf", ".docx", ".txt", ".md")):
        return "Documents"
    elif name.endswith((".xlsx", ".csv")):
        return "Spreadsheets"
    elif name.endswith((".mp3", ".wav")):
        return "Music"
    elif name.endswith((".mp4", ".mov")):
        return "Videos"
    elif name.endswith((".dmg", ".exe", ".pkg", ".msi")):
        return "Installers"
    elif name.endswith((".zip", ".tar", ".gz")):
        return "Archives"
    else:
        return "Other"


def create_practice_mess():
    """Build (or rebuild) the sandbox so there's always something to tidy."""
    PRACTICE_FOLDER.mkdir(exist_ok=True)      # ok if it already exists
    made = 0
    for filename in SAMPLE_FILES:
        file = PRACTICE_FOLDER / filename
        if not file.exists():                 # don't clobber student edits
            file.write_text(f"pretend contents of {filename}\n")
            made += 1
    if made:
        print(f"Sandbox ready: created {made} practice file(s) in {PRACTICE_FOLDER.name}/")


def organize(folder, apply_changes):
    """Plan (and optionally perform) the tidy-up of one folder."""
    # Lesson 04's iterdir, filtered to loose files (folders stay put).
    files = sorted(item for item in folder.iterdir()
                   if item.is_file() and not item.name.startswith("."))
    # ^ skipping dot-files (hidden system files) — a tiny act of caution
    #   you should look for in any AI script that touches folders.

    if not files:
        print(f"Nothing to organize in {folder} — it's already tidy!")
        return

    mode = "MOVING" if apply_changes else "DRY RUN — planning only, nothing moves"
    print(f"\n{mode}: {len(files)} file(s) in {folder}\n")

    moved_counts = {}                          # lesson 02's tally pattern
    for file in files:
        destination_folder = folder / folder_for(file.name)
        destination = destination_folder / file.name
        print(f"  {file.name:<24} ->  {destination_folder.name}/")

        if apply_changes:
            destination_folder.mkdir(exist_ok=True)
            if destination.exists():
                print(f"    ^ skipped: {destination_folder.name}/ already has one")
                continue                       # never silently overwrite
            file.rename(destination)           # rename = how Python moves files
        moved_counts[destination_folder.name] = moved_counts.get(destination_folder.name, 0) + 1

    # ── PREDICT: which folder wins the tally? Count the extensions above! ──
    print("\nSummary:")
    for folder_name, how_many in sorted(moved_counts.items()):
        print(f"  {folder_name:<14} {how_many} file(s)")

    if not apply_changes:
        print("\nThat was the plan. Happy with it? Rerun with --apply to make it real.")
    else:
        print("\nDone! Open the folder and admire the order.")


def main():
    # argparse reads the flags you typed after the script name.
    # Why you care: --dry-run/--apply flags are the steering wheel of
    # every AI-generated automation — always check which is the default.
    parser = argparse.ArgumentParser(description="Tidy a messy folder by file type.")
    parser.add_argument("--apply", action="store_true",
                        help="actually move files (default: dry run)")
    parser.add_argument("--real", action="store_true",
                        help="use your REAL ~/Downloads instead of the sandbox")
    args = parser.parse_args()

    if args.real:
        folder = Path.home() / "Downloads"
        if not folder.exists():
            print(f"No Downloads folder found at {folder} — try the sandbox instead.")
            raise SystemExit(1)
        if args.apply:
            # An interactive last line of defense before touching real files.
            print(f"About to REALLY move files inside {folder}.")
            answer = input("Type YES to continue, anything else to bail out: ")
            if answer.strip() != "YES":
                print("Wise. Nothing was touched.")
                raise SystemExit(0)
    else:
        create_practice_mess()
        folder = PRACTICE_FOLDER

    # ── PREDICT: you ran with no flags. Does anything move? ──
    organize(folder, apply_changes=args.apply)


if __name__ == "__main__":   # "only run main() when executed as a script"
    main()

# ✏️ TRY IT:
#   1. Run the sandbox dry run, then --apply, then dry run again —
#      read all three outputs. Delete practice_downloads/ to reset.
#   2. Add a rule to folder_for: route ".pptx" to "Presentations",
#      then add "pitch_deck.pptx" to SAMPLE_FILES and rerun.
#   3. When you trust it: --real (still just a plan!), read the plan
#      carefully, and only then decide about --real --apply.
#   4. Graduation: paste this file into an AI chat and ask it to also
#      sort files into by-month subfolders. Then READ the diff before
#      running — Spot, Compose, Request, Inspect, Prove. You know the loop.
