# /// script
# requires-python = ">=3.12"
# ///
"""Organize a messy folder by sorting files into subfolders by type.

Input   -> a folder full of mixed files (practice on ./practice-mess first!)
Process -> pick a destination subfolder from each file's extension
Output  -> files moved into documents/ PDFs/ images/ data/ media/ archives/

Safe by default: it only PREVIEWS the moves. Pass --apply to actually move files.

Run it like:
    uv run demos/reserve/downloads-organizer/organize.py practice-mess
    uv run demos/reserve/downloads-organizer/organize.py practice-mess --apply

Needs: nothing (no API key).
"""

import argparse
import shutil
import sys
from pathlib import Path

# The whole "brain" of this tool is one dictionary: extension -> subfolder name.
# Want different rules? Edit this table — no other code needs to change.
EXTENSION_FOLDERS = {
    ".txt": "documents",
    ".md": "documents",
    ".docx": "documents",
    ".log": "documents",
    ".pdf": "PDFs",
    ".png": "images",
    ".jpg": "images",
    ".jpeg": "images",
    ".gif": "images",
    ".heic": "images",
    ".csv": "data",
    ".xlsx": "data",
    ".json": "data",
    ".mp3": "media",
    ".mp4": "media",
    ".mov": "media",
    ".zip": "archives",
}


def organize_files(folder: Path, apply: bool) -> None:
    moved = skipped = 0

    # iterdir() lists the folder's direct children; we ignore subfolders so the
    # script never wanders deeper than the one folder you pointed it at.
    for file in sorted(folder.iterdir()):
        if not file.is_file():
            continue

        target = EXTENSION_FOLDERS.get(file.suffix.lower())
        if target is None:
            print(f"skip        {file.name}  (no rule for '{file.suffix}')")
            skipped += 1
            continue

        if apply:
            destination = folder / target
            destination.mkdir(exist_ok=True)
            shutil.move(str(file), str(destination / file.name))
            print(f"moved       {file.name}  ->  {target}/")
        else:
            print(f"would move  {file.name}  ->  {target}/")
        moved += 1

    verb = "moved" if apply else "would move"
    print(f"\nSummary: {verb} {moved} file(s), skipped {skipped}.")
    if not apply:
        print("This was a DRY RUN — nothing changed. Re-run with --apply to move files.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sort files in a folder into subfolders by type.")
    parser.add_argument("folder", help="Path to the folder to organize, e.g. practice-mess")
    parser.add_argument("--apply", action="store_true",
                        help="Actually move files (default: preview only)")
    args = parser.parse_args()

    folder = Path(args.folder).expanduser()
    if not folder.is_dir():
        print(f"That folder does not exist: {folder}")
        print("Tip: build a safe practice folder first with:")
        print("     uv run demos/reserve/downloads-organizer/make_mess.py --apply")
        sys.exit(1)

    organize_files(folder, apply=args.apply)


if __name__ == "__main__":
    main()
