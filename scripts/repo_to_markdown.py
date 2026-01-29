#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Fetch contents of .md, .py, and .ipynb files from a repository
and combine them into a single markdown file.

Usage:
    uv run repo_to_markdown.py /path/to/repo
    uv run repo_to_markdown.py /path/to/repo -o output.md
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime


EXTENSIONS = {'.md', '.py', '.ipynb'}

EXCLUDED_DIRS = {
    '.git', '__pycache__', 'node_modules', '.venv', 'venv', 
    'env', '.env', '.idea', '.vscode', 'dist', 'build', 
    'egg-info', '.eggs', '.tox', '.pytest_cache'
}


def should_include_file(filepath: Path) -> bool:
    """Check if file should be included based on extension."""
    return filepath.suffix.lower() in EXTENSIONS


def should_skip_directory(dirname: str) -> bool:
    """Check if directory should be skipped."""
    return dirname in EXCLUDED_DIRS or dirname.startswith('.')


def read_file_contents(filepath: Path) -> str:
    """Read and return file contents, handling different file types."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # For Jupyter notebooks, extract a readable format
        if filepath.suffix.lower() == '.ipynb':
            return format_notebook(content, filepath)
        
        return content
    except UnicodeDecodeError:
        return f"[Error: Could not decode file as UTF-8]"
    except Exception as e:
        return f"[Error reading file: {e}]"


def format_notebook(content: str, filepath: Path) -> str:
    """Format Jupyter notebook content into readable markdown."""
    try:
        notebook = json.loads(content)
        cells = notebook.get('cells', [])
        
        formatted_parts = []
        for i, cell in enumerate(cells):
            cell_type = cell.get('cell_type', 'unknown')
            source = ''.join(cell.get('source', []))
            
            if cell_type == 'markdown':
                formatted_parts.append(source)
            elif cell_type == 'code':
                formatted_parts.append(f"```python\n{source}\n```")
            elif cell_type == 'raw':
                formatted_parts.append(f"```\n{source}\n```")
        
        return '\n\n'.join(formatted_parts)
    except json.JSONDecodeError:
        return f"[Error: Invalid JSON in notebook]"
    except Exception as e:
        return f"[Error parsing notebook: {e}]"


def get_language_for_extension(ext: str) -> str:
    """Return the markdown code fence language for a file extension."""
    mapping = {
        '.py': 'python',
        '.md': 'markdown',
    }
    return mapping.get(ext.lower(), '')


def collect_files(repo_path: Path) -> list[tuple[Path, str]]:
    """Walk the repo and collect all matching files with their contents."""
    files_collected = []
    
    for root, dirs, files in os.walk(repo_path):
        # Filter out excluded directories (modifies dirs in-place)
        dirs[:] = [d for d in dirs if not should_skip_directory(d)]
        dirs.sort()  # Consistent ordering
        
        root_path = Path(root)
        
        for filename in sorted(files):
            filepath = root_path / filename
            
            if should_include_file(filepath):
                relative_path = filepath.relative_to(repo_path)
                content = read_file_contents(filepath)
                files_collected.append((relative_path, content))
    
    return files_collected


def generate_markdown(repo_path: Path, files: list[tuple[Path, str]]) -> str:
    """Generate the combined markdown output."""
    lines = [
        f"# Repository Contents: {repo_path.name}",
        f"",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
        f"**Files included:** `.md`, `.py`, `.ipynb`",
        f"",
        f"**Total files:** {len(files)}",
        f"",
        "---",
        "",
        "## Table of Contents",
        "",
    ]
    
    # Generate TOC
    for i, (relative_path, _) in enumerate(files, 1):
        anchor = str(relative_path).replace('/', '-').replace('.', '-').replace('_', '-').lower()
        lines.append(f"{i}. [{relative_path}](#{anchor})")
    
    lines.extend(["", "---", ""])
    
    # Generate file contents
    for relative_path, content in files:
        ext = relative_path.suffix.lower()
        
        lines.append(f"## {relative_path}")
        lines.append("")
        
        if ext == '.ipynb':
            # Notebook content is already formatted as markdown
            lines.append(content)
        elif ext == '.md':
            # For markdown files, include as-is but in a details block to avoid formatting conflicts
            lines.append("<details>")
            lines.append(f"<summary>View {relative_path.name}</summary>")
            lines.append("")
            lines.append(content)
            lines.append("")
            lines.append("</details>")
        else:
            # For code files, wrap in code fence
            lang = get_language_for_extension(ext)
            lines.append(f"```{lang}")
            lines.append(content)
            lines.append("```")
        
        lines.extend(["", "---", ""])
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Combine .md, .py, and .ipynb files from a repo into a single markdown file.'
    )
    parser.add_argument(
        'repo_path',
        type=str,
        help='Path to the repository root'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output file path (default: <repo_name>_contents.md)'
    )
    parser.add_argument(
        '--no-notebooks',
        action='store_true',
        help='Exclude .ipynb files'
    )
    parser.add_argument(
        '--no-markdown',
        action='store_true',
        help='Exclude .md files'
    )
    parser.add_argument(
        '--no-python',
        action='store_true',
        help='Exclude .py files'
    )
    
    args = parser.parse_args()
    
    # Modify extensions based on flags
    if args.no_notebooks:
        EXTENSIONS.discard('.ipynb')
    if args.no_markdown:
        EXTENSIONS.discard('.md')
    if args.no_python:
        EXTENSIONS.discard('.py')
    
    repo_path = Path(args.repo_path).resolve()
    
    if not repo_path.exists():
        print(f"Error: Path '{repo_path}' does not exist.")
        return 1
    
    if not repo_path.is_dir():
        print(f"Error: Path '{repo_path}' is not a directory.")
        return 1
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(f"{repo_path.name}_contents.md")
    
    print(f"Scanning: {repo_path}")
    print(f"Extensions: {', '.join(sorted(EXTENSIONS))}")
    
    # Collect files
    files = collect_files(repo_path)
    print(f"Found {len(files)} files")
    
    # Generate markdown
    markdown_content = generate_markdown(repo_path, files)
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"Output written to: {output_path}")
    return 0


if __name__ == '__main__':
    exit(main())