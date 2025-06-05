#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import os
import shutil
from datetime import datetime

# Config
SOURCE_FOLDER = "/Users/greatmaster/Desktop/projects/oreilly-live-trainings/oreilly-python-course"
DEST_FOLDER = "/Users/greatmaster/Desktop/projects/tmp_files"
TODAY = datetime.today().strftime('%Y-%m-%d')

# Create destination if it doesn't exist
os.makedirs(DEST_FOLDER, exist_ok=True)

# Walk the source folder
for root, dirs, files in os.walk(SOURCE_FOLDER):
    # Limit folder depth to 2 below source (so total 3: base + 2)
    depth = root[len(SOURCE_FOLDER):].count(os.sep)
    if depth > 2:
        continue

    # Compute relative path and new destination
    rel_path = os.path.relpath(root, SOURCE_FOLDER)
    target_dir = os.path.join(DEST_FOLDER, rel_path)
    os.makedirs(target_dir, exist_ok=True)

    # Copy and rename files
    for file in files:
        src_file = os.path.join(root, file)
        new_filename = f"{TODAY}_{file}"
        dst_file = os.path.join(target_dir, new_filename)
        shutil.copy2(src_file, dst_file)

print(f"Backup completed with date-prefix '{TODAY}'.")
