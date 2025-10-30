#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "rich>=13.0.0",
# ]
# ///
"""
Smart File Organizer - Automatically organize files by type, date, or size
Usage: python smart_file_organizer.py [directory] [--mode=type|date|size]
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import argparse
from rich.console import Console
from rich.table import Table
from rich.progress import track

console = Console()

# File type categories
FILE_CATEGORIES = {
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".pages"],
    "Spreadsheets": [".xls", ".xlsx", ".csv", ".ods", ".numbers"],
    "Presentations": [".ppt", ".pptx", ".key", ".odp"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".heic"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".webm"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg", ".wma"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".go", ".rs"],
    "Executables": [".exe", ".app", ".dmg", ".pkg", ".deb", ".rpm"],
    "Other": []
}


def get_category(file_extension: str) -> str:
    """Determine the category for a file based on its extension."""
    file_extension = file_extension.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if file_extension in extensions:
            return category
    return "Other"


def organize_by_type(source_dir: Path, dry_run: bool = False) -> Dict[str, int]:
    """Organize files by their type into categorized folders."""
    stats = {}
    files = [f for f in source_dir.iterdir() if f.is_file() and not f.name.startswith('.')]

    for file_path in track(files, description="Organizing by type..."):
        extension = file_path.suffix
        category = get_category(extension)

        target_dir = source_dir / category
        target_path = target_dir / file_path.name

        # Handle duplicates
        counter = 1
        while target_path.exists():
            stem = file_path.stem
            target_path = target_dir / f"{stem}_{counter}{extension}"
            counter += 1

        if not dry_run:
            target_dir.mkdir(exist_ok=True)
            shutil.move(str(file_path), str(target_path))

        stats[category] = stats.get(category, 0) + 1

    return stats


def organize_by_date(source_dir: Path, dry_run: bool = False) -> Dict[str, int]:
    """Organize files by modification date (Year/Month structure)."""
    stats = {}
    files = [f for f in source_dir.iterdir() if f.is_file() and not f.name.startswith('.')]

    for file_path in track(files, description="Organizing by date..."):
        mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        year_month = mod_time.strftime("%Y/%Y-%m-%B")

        target_dir = source_dir / year_month
        target_path = target_dir / file_path.name

        # Handle duplicates
        counter = 1
        while target_path.exists():
            stem = file_path.stem
            extension = file_path.suffix
            target_path = target_dir / f"{stem}_{counter}{extension}"
            counter += 1

        if not dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file_path), str(target_path))

        stats[year_month] = stats.get(year_month, 0) + 1

    return stats


def organize_by_size(source_dir: Path, dry_run: bool = False) -> Dict[str, int]:
    """Organize files by size categories."""
    stats = {}
    files = [f for f in source_dir.iterdir() if f.is_file() and not f.name.startswith('.')]

    size_categories = {
        "Tiny (< 100KB)": (0, 100 * 1024),
        "Small (100KB - 1MB)": (100 * 1024, 1024 * 1024),
        "Medium (1MB - 10MB)": (1024 * 1024, 10 * 1024 * 1024),
        "Large (10MB - 100MB)": (10 * 1024 * 1024, 100 * 1024 * 1024),
        "Huge (> 100MB)": (100 * 1024 * 1024, float('inf'))
    }

    for file_path in track(files, description="Organizing by size..."):
        file_size = file_path.stat().st_size

        for category, (min_size, max_size) in size_categories.items():
            if min_size <= file_size < max_size:
                target_dir = source_dir / category
                target_path = target_dir / file_path.name

                # Handle duplicates
                counter = 1
                while target_path.exists():
                    stem = file_path.stem
                    extension = file_path.suffix
                    target_path = target_dir / f"{stem}_{counter}{extension}"
                    counter += 1

                if not dry_run:
                    target_dir.mkdir(exist_ok=True)
                    shutil.move(str(file_path), str(target_path))

                stats[category] = stats.get(category, 0) + 1
                break

    return stats


def display_stats(stats: Dict[str, int], mode: str):
    """Display organization statistics in a nice table."""
    table = Table(title=f"Organization Results - {mode.upper()} Mode")
    table.add_column("Category/Folder", style="cyan")
    table.add_column("Files Moved", style="green", justify="right")

    for category, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        table.add_row(category, str(count))

    table.add_row("TOTAL", str(sum(stats.values())), style="bold yellow")
    console.print(table)


def main():
    parser = argparse.ArgumentParser(
        description="Smart File Organizer - Organize files intelligently"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to organize (default: current directory)"
    )
    parser.add_argument(
        "--mode",
        choices=["type", "date", "size"],
        default="type",
        help="Organization mode (default: type)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without moving files"
    )

    args = parser.parse_args()
    source_dir = Path(args.directory).resolve()

    if not source_dir.exists():
        console.print(f"[red]Error: Directory '{source_dir}' does not exist[/red]")
        return

    if not source_dir.is_dir():
        console.print(f"[red]Error: '{source_dir}' is not a directory[/red]")
        return

    console.print(f"\n[bold cyan]Smart File Organizer[/bold cyan]")
    console.print(f"Directory: {source_dir}")
    console.print(f"Mode: {args.mode}")
    console.print(f"Dry Run: {args.dry_run}\n")

    if args.dry_run:
        console.print("[yellow]DRY RUN MODE - No files will be moved[/yellow]\n")

    # Organize based on selected mode
    if args.mode == "type":
        stats = organize_by_type(source_dir, args.dry_run)
    elif args.mode == "date":
        stats = organize_by_date(source_dir, args.dry_run)
    else:  # size
        stats = organize_by_size(source_dir, args.dry_run)

    # Display results
    display_stats(stats, args.mode)

    if args.dry_run:
        console.print("\n[yellow]This was a dry run. Use without --dry-run to actually move files.[/yellow]")
    else:
        console.print("\n[green]Organization complete![/green]")


if __name__ == "__main__":
    main()
