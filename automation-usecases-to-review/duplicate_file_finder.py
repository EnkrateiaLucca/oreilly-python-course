#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "rich>=13.0.0",
# ]
# ///
"""
Duplicate File Finder - Find and remove duplicate files based on content hash
Usage: python duplicate_file_finder.py [directory] [--delete]
"""

import os
import hashlib
from pathlib import Path
from typing import Dict, List
import argparse
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.prompt import Confirm

console = Console()


def calculate_file_hash(file_path: Path, chunk_size: int = 8192) -> str:
    """Calculate MD5 hash of a file."""
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (IOError, OSError) as e:
        console.print(f"[yellow]Warning: Could not read {file_path}: {e}[/yellow]")
        return None


def find_duplicates(directory: Path, recursive: bool = True) -> Dict[str, List[Path]]:
    """Find duplicate files in a directory."""
    hash_map = defaultdict(list)

    # Get all files
    if recursive:
        files = list(directory.rglob("*"))
    else:
        files = list(directory.glob("*"))

    files = [f for f in files if f.is_file() and not f.name.startswith('.')]

    console.print(f"\n[cyan]Scanning {len(files)} files...[/cyan]\n")

    # Calculate hashes
    for file_path in track(files, description="Calculating hashes..."):
        file_hash = calculate_file_hash(file_path)
        if file_hash:
            hash_map[file_hash].append(file_path)

    # Filter to only duplicates (more than one file with same hash)
    duplicates = {k: v for k, v in hash_map.items() if len(v) > 1}

    return duplicates


def get_file_size_str(size_bytes: int) -> str:
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def display_duplicates(duplicates: Dict[str, List[Path]]):
    """Display duplicate files in a nice format."""
    total_duplicates = sum(len(files) - 1 for files in duplicates.values())
    total_wasted_space = sum(
        files[0].stat().st_size * (len(files) - 1)
        for files in duplicates.values()
    )

    console.print(f"\n[bold yellow]Found {len(duplicates)} sets of duplicates "
                  f"({total_duplicates} duplicate files)[/bold yellow]")
    console.print(f"[bold red]Wasted space: {get_file_size_str(total_wasted_space)}[/bold red]\n")

    for idx, (file_hash, files) in enumerate(duplicates.items(), 1):
        file_size = files[0].stat().st_size
        wasted_space = file_size * (len(files) - 1)

        table = Table(
            title=f"Duplicate Set #{idx} - {len(files)} copies - "
                  f"Size: {get_file_size_str(file_size)} - "
                  f"Wasted: {get_file_size_str(wasted_space)}",
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("#", style="cyan", width=4)
        table.add_column("File Path", style="white")
        table.add_column("Modified", style="yellow")

        for i, file_path in enumerate(sorted(files, key=lambda x: x.stat().st_mtime), 1):
            mod_time = file_path.stat().st_mtime
            mod_date = Path(file_path).stat().st_mtime
            from datetime import datetime
            mod_str = datetime.fromtimestamp(mod_date).strftime("%Y-%m-%d %H:%M")

            # Highlight the oldest file (keeper)
            style = "green" if i == 1 else "white"
            table.add_row(str(i), str(file_path), mod_str, style=style)

        console.print(table)
        console.print()


def delete_duplicates(duplicates: Dict[str, List[Path]], keep_strategy: str = "oldest"):
    """Delete duplicate files, keeping one based on strategy."""
    total_deleted = 0
    total_space_freed = 0

    console.print(f"\n[yellow]Deletion strategy: Keep the {keep_strategy} file[/yellow]\n")

    for file_hash, files in duplicates.items():
        # Sort files based on strategy
        if keep_strategy == "oldest":
            files.sort(key=lambda x: x.stat().st_mtime)
        elif keep_strategy == "newest":
            files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        else:  # first
            pass

        keeper = files[0]
        to_delete = files[1:]

        console.print(f"[green]Keeping:[/green] {keeper}")

        for file_path in to_delete:
            try:
                file_size = file_path.stat().st_size
                file_path.unlink()
                console.print(f"[red]Deleted:[/red] {file_path}")
                total_deleted += 1
                total_space_freed += file_size
            except OSError as e:
                console.print(f"[red]Error deleting {file_path}: {e}[/red]")

        console.print()

    console.print(f"[bold green]Deleted {total_deleted} duplicate files[/bold green]")
    console.print(f"[bold green]Freed {get_file_size_str(total_space_freed)}[/bold green]")


def export_report(duplicates: Dict[str, List[Path]], output_file: Path):
    """Export duplicate file report to a text file."""
    with open(output_file, 'w') as f:
        f.write("Duplicate Files Report\n")
        f.write("=" * 80 + "\n\n")

        for idx, (file_hash, files) in enumerate(duplicates.items(), 1):
            file_size = files[0].stat().st_size
            f.write(f"Duplicate Set #{idx} ({len(files)} copies)\n")
            f.write(f"Hash: {file_hash}\n")
            f.write(f"Size: {get_file_size_str(file_size)}\n")
            f.write("-" * 80 + "\n")

            for i, file_path in enumerate(files, 1):
                f.write(f"  {i}. {file_path}\n")

            f.write("\n")

    console.print(f"[green]Report saved to: {output_file}[/green]")


def main():
    parser = argparse.ArgumentParser(
        description="Duplicate File Finder - Find and remove duplicate files"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to scan (default: current directory)"
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        default=True,
        help="Scan subdirectories recursively (default: True)"
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete duplicate files (will prompt for confirmation)"
    )
    parser.add_argument(
        "--keep",
        choices=["oldest", "newest", "first"],
        default="oldest",
        help="Which file to keep when deleting duplicates (default: oldest)"
    )
    parser.add_argument(
        "--export",
        type=str,
        help="Export report to file"
    )

    args = parser.parse_args()
    directory = Path(args.directory).resolve()

    if not directory.exists():
        console.print(f"[red]Error: Directory '{directory}' does not exist[/red]")
        return

    console.print(f"\n[bold cyan]Duplicate File Finder[/bold cyan]")
    console.print(f"Directory: {directory}")
    console.print(f"Recursive: {args.recursive}\n")

    # Find duplicates
    duplicates = find_duplicates(directory, args.recursive)

    if not duplicates:
        console.print("[green]No duplicate files found![/green]")
        return

    # Display results
    display_duplicates(duplicates)

    # Export report if requested
    if args.export:
        export_file = Path(args.export)
        export_report(duplicates, export_file)

    # Delete duplicates if requested
    if args.delete:
        console.print("\n[bold red]WARNING: This will permanently delete duplicate files![/bold red]")
        if Confirm.ask("Do you want to proceed with deletion?"):
            delete_duplicates(duplicates, args.keep)
        else:
            console.print("[yellow]Deletion cancelled[/yellow]")
    else:
        console.print("\n[yellow]Use --delete flag to remove duplicate files[/yellow]")


if __name__ == "__main__":
    main()
