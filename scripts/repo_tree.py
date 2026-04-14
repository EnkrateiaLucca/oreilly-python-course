#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Generate a tree-like structure of a directory/repository.

Usage:
    uv run repo_tree.py [path] [options]
    
Examples:
    uv run repo_tree.py .
    uv run repo_tree.py /path/to/repo --exclude __pycache__ .git
    uv run repo_tree.py . --show-hidden
"""

import argparse
import os
from pathlib import Path


DEFAULT_EXCLUDES = {
    "__pycache__",
    ".git",
    ".svn",
    ".hg",
    "node_modules",
    ".venv",
    "venv",
    ".env",
    ".idea",
    ".vscode",
    ".DS_Store",
    "*.pyc",
    "*.pyo",
}


def should_exclude(name: str, exclude_patterns: set[str]) -> bool:
    """Check if a file/folder should be excluded."""
    if name in exclude_patterns:
        return True
    for pattern in exclude_patterns:
        if pattern.startswith("*") and name.endswith(pattern[1:]):
            return True
    return False


def generate_tree(
    root_path: Path,
    prefix: str = "",
    exclude_patterns: set[str] | None = None,
    show_hidden: bool = False,
) -> list[str]:
    """
    Generate a tree structure for the given directory.
    
    Args:
        root_path: The root directory to generate tree for
        prefix: Current prefix for tree branches
        exclude_patterns: Set of patterns to exclude
        show_hidden: Whether to show hidden files/folders
        
    Returns:
        List of strings representing the tree structure
    """
    if exclude_patterns is None:
        exclude_patterns = DEFAULT_EXCLUDES
    
    lines = []
    
    try:
        entries = list(root_path.iterdir())
    except PermissionError:
        return [f"{prefix}[Permission Denied]"]
    
    # Filter entries
    filtered_entries = []
    for entry in entries:
        name = entry.name
        
        # Skip hidden files unless requested
        if not show_hidden and name.startswith("."):
            continue
            
        # Skip excluded patterns
        if should_exclude(name, exclude_patterns):
            continue
            
        filtered_entries.append(entry)
    
    # Sort: directories first, then files, both alphabetically
    filtered_entries.sort(key=lambda e: (not e.is_dir(), e.name.lower()))
    
    # Tree characters
    BRANCH = "├── "
    LAST_BRANCH = "└── "
    VERTICAL = "│   "
    SPACE = "    "
    
    for i, entry in enumerate(filtered_entries):
        is_last = i == len(filtered_entries) - 1
        connector = LAST_BRANCH if is_last else BRANCH
        
        lines.append(f"{prefix}{connector}{entry.name}")
        
        if entry.is_dir():
            # Recursively process subdirectory
            extension = SPACE if is_last else VERTICAL
            subtree = generate_tree(
                entry,
                prefix=prefix + extension,
                exclude_patterns=exclude_patterns,
                show_hidden=show_hidden,
            )
            lines.extend(subtree)
    
    return lines


def print_tree(
    root_path: str | Path,
    exclude_patterns: set[str] | None = None,
    show_hidden: bool = False,
) -> str:
    """
    Generate and return the full tree as a string.
    
    Args:
        root_path: Path to the root directory
        exclude_patterns: Patterns to exclude (uses defaults if None)
        show_hidden: Whether to include hidden files
        
    Returns:
        Complete tree structure as a string
    """
    root = Path(root_path).resolve()
    
    if not root.exists():
        return f"Error: Path '{root}' does not exist"
    
    if not root.is_dir():
        return f"Error: Path '{root}' is not a directory"
    
    lines = [root.name]
    tree_lines = generate_tree(
        root,
        exclude_patterns=exclude_patterns,
        show_hidden=show_hidden,
    )
    lines.extend(tree_lines)
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a tree-like structure of a directory/repository"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Root directory path (default: current directory)",
    )
    parser.add_argument(
        "--exclude",
        "-e",
        nargs="*",
        default=None,
        help="Additional patterns to exclude",
    )
    parser.add_argument(
        "--no-default-excludes",
        action="store_true",
        help="Don't use default exclusion patterns",
    )
    parser.add_argument(
        "--show-hidden",
        "-a",
        action="store_true",
        help="Show hidden files and directories",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file (default: print to stdout)",
    )
    
    args = parser.parse_args()
    
    # Build exclusion patterns
    if args.no_default_excludes:
        exclude_patterns = set()
    else:
        exclude_patterns = DEFAULT_EXCLUDES.copy()
    
    if args.exclude:
        exclude_patterns.update(args.exclude)
    
    # Generate tree
    tree = print_tree(
        args.path,
        exclude_patterns=exclude_patterns,
        show_hidden=args.show_hidden,
    )
    
    # Output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(tree)
        print(f"Tree written to {args.output}")
    else:
        print(tree)


if __name__ == "__main__":
    main()