# /// script
# requires-python = ">=3.10"
# ///
"""Organize a messy folder by sorting files into subfolders by type.

Automation category: File management.

Input   -> a folder full of mixed files
Process -> decide a destination subfolder from each file's extension
Output  -> files moved into documents/ PDFs/ images/ data/

Safe by default: it only PREVIEWS the moves. Pass --apply to actually move files.

Run it like:
    uv run scripts/demos/file-management/organize_folder.py ~/Downloads
    uv run scripts/demos/file-management/organize_folder.py ~/Downloads --apply

Needs: nothing (no API key).
"""

import argparse
import shutil
from pathlib import Path

# Which subfolder each file extension should be moved into.
EXTENSION_FOLDERS = {
    ".txt": "documents",
    ".md": "documents",
    ".pdf": "PDFs",
    ".png": "images",
    ".jpg": "images",
    ".jpeg": "images",
    ".csv": "data",
    ".xlsx": "data",
}


def organize_files(folder: Path, apply: bool) -> None:
    for file in folder.iterdir():
        if not file.is_file():
            continue  # skip subfolders

        target = EXTENSION_FOLDERS.get(file.suffix.lower())
        if target is None:
            print(f"skip        {file.name}  (no rule for '{file.suffix}')")
            continue

        if apply:
            destination = folder / target
            destination.mkdir(exist_ok=True)
            shutil.move(str(file), str(destination / file.name))
            print(f"moved       {file.name}  ->  {target}/")
        else:
            print(f"would move  {file.name}  ->  {target}/")

    if not apply:
        print("\nThis was a dry run. Re-run with --apply to actually move the files.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sort files in a folder into subfolders by type.")
    parser.add_argument("folder", help="Path to the folder to organize, e.g. ~/Downloads")
    parser.add_argument("--apply", action="store_true", help="Actually move files (default: preview only)")
    args = parser.parse_args()

    organize_files(Path(args.folder).expanduser(), apply=args.apply)
