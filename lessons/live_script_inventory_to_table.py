"""
Folder inventory -> CSV

Reads the contents of a folder (top level only), sorts each item into a
category, and writes the result to a .csv file using pandas.

This script is READ-ONLY with respect to the folder it scans: it never
deletes, moves, or renames anything. The only file it writes is the CSV.

Imports: os and pandas only.

Usage (manual trigger):
    python folder_inventory.py
"""

import os

import pandas as pd

# --- settings: edit these instead of passing command-line flags ---
ROOT_FOLDER = "./"
OUTPUT_CSV = "folder_inventory.csv"
INCLUDE_HIDDEN = False  # set to True to include items starting with a dot
# ------------------------------------------------------------------

CATEGORY_ORDER = ["Folder", "Python file", "Markdown file", "Other file"]


def categorize(name, full_path):
    """Return a category string for one item."""
    if os.path.isdir(full_path):
        return "Folder"
    elif name.endswith(".py"):
        return "Python file"
    elif name.endswith(".md"):
        return "Markdown file"
    else:
        return "Other file"


def build_inventory(root_folder, output_csv, include_hidden):
    """Walk the top level of root_folder and return a list of row dicts."""
    rows = []

    items = os.listdir(root_folder)

    for item in items:
        # skip dotfiles like .git or .env unless we asked for them
        if not include_hidden and item.startswith("."):
            continue

        # skip the CSV we are about to write, so re-runs stay clean
        if item == os.path.basename(output_csv):
            continue

        full_path = os.path.join(root_folder, item)
        category = categorize(item, full_path)

        if category == "Folder":
            extension = ""
            size_bytes = ""
        else:
            # splitext splits "notes.md" into ("notes", ".md")
            extension = os.path.splitext(item)[1]
            size_bytes = os.path.getsize(full_path)

        rows.append({
            "name": item,
            "category": category,
            "extension": extension,
            "size_bytes": size_bytes,
            "path": full_path,
        })

    return rows


rows = build_inventory(ROOT_FOLDER, OUTPUT_CSV, INCLUDE_HIDDEN)

df = pd.DataFrame(rows, columns=["name", "category", "extension", "size_bytes", "path"])

# If this is NOT empty do this....
if not df.empty:
    # Categorical makes the sort follow CATEGORY_ORDER instead of the alphabet
    df["category"] = pd.Categorical(df["category"], categories=CATEGORY_ORDER, ordered=True)
    df = df.sort_values(["category", "name"]).reset_index(drop=True)

df.to_csv(OUTPUT_CSV, index=False)

# summary printed to the terminal
print("# Folder Inventory")
print("Scanned:", os.path.abspath(ROOT_FOLDER))
# size of the table (in number of rows)
print("Items:  ", len(df))
if not df.empty:
    for category, count in df["category"].value_counts().sort_index().items():
        print("  -", category + ":", count)
print("Saved:  ", os.path.abspath(OUTPUT_CSV))