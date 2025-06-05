#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["nbformat"]
# ///

import sys
import os
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

def markdown_to_notebook(md_path: str, ipynb_path: str = None):
    if not os.path.isfile(md_path):
        raise FileNotFoundError(f"Markdown file not found: {md_path}")
    
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    nb_cells = []
    in_code_block = False
    code_block_lang = ""
    code_lines = []
    markdown_lines = []

    def flush_markdown():
        nonlocal markdown_lines
        if markdown_lines:
            nb_cells.append(new_markdown_cell("".join(markdown_lines)))
            markdown_lines = []

    def flush_code():
        nonlocal code_lines
        if code_lines:
            nb_cells.append(new_code_cell("".join(code_lines)))
            code_lines = []

    for line in lines:
        if line.strip().startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_block_lang = line.strip()[3:]
                flush_markdown()
            else:
                in_code_block = False
                flush_code()
        elif in_code_block:
            code_lines.append(line)
        else:
            markdown_lines.append(line)

    flush_markdown()

    nb = new_notebook(cells=nb_cells)
    output_path = ipynb_path or md_path.rsplit(".", 1)[0] + ".ipynb"
    with open(output_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)

    print(f"Notebook written to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run script.py <input_markdown.md> [output_notebook.ipynb]")
        sys.exit(1)
    md_path = sys.argv[1]
    ipynb_path = sys.argv[2] if len(sys.argv) > 2 else None
    markdown_to_notebook(md_path, ipynb_path)
