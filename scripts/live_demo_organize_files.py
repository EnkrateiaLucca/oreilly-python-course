# /// script
# requires-python = ">=3.12"
# ///

import os
import shutil
from pathlib import Path
import sys

def organize_files_in_folder(folder_path):
    """
    Organize files in the given folder into three subfolders:
    - documents: .md, .txt, .pdf
    - media: .png, .jpg, .jpeg, .gif, .bmp, .tiff, .svg, .webp
    - others: any other file types or files without extension

    Only top-level files in folder_path are moved (subfolders are left intact).
    If a filename conflict occurs in the destination folder, a numeric suffix is added.
    Returns a success message with counts of moved files.
    """
    folder = Path(folder_path)

    if not folder.exists() or not folder.is_dir():
        return f"Error: '{folder_path}' does not exist or is not a directory."

    # Define extension sets
    documents_ext = {'.md', '.txt', '.pdf'}
    media_ext = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.svg', '.webp'}

    # Create destination folders
    documents_dir = folder / "documents"
    media_dir = folder / "media"
    others_dir = folder / "others"

    for d in (documents_dir, media_dir, others_dir):
        d.mkdir(exist_ok=True)

    moved_counts = {"documents": 0, "media": 0, "others": 0}

    for entry in folder.iterdir():
        # Only process files at the top level (skip directories)
        if not entry.is_file():
            continue

        # Skip files that are already inside one of the target folders
        if entry.parent in (documents_dir, media_dir, others_dir):
            continue

        ext = entry.suffix.lower()

        # Decide destination based on extension
        if ext in documents_ext:
            dest_dir = documents_dir
            key = "documents"
        elif ext in media_ext:
            dest_dir = media_dir
            key = "media"
        else:
            dest_dir = others_dir
            key = "others"

        # Resolve name conflicts by adding a suffix before the extension
        dest_path = dest_dir / entry.name
        if dest_path.exists():
            stem = entry.stem
            suffix = entry.suffix
            counter = 1
            while True:
                new_name = f"{stem}({counter}){suffix}"
                dest_path = dest_dir / new_name
                if not dest_path.exists():
                    break
                counter += 1

        # Move the file
        try:
            shutil.move(str(entry), str(dest_path))
            moved_counts[key] += 1
        except Exception as e:
            # If a file couldn't be moved, continue with others
            print(f"Warning: could not move '{entry.name}': {e}")

    return (f"Files organized successfully. Moved {moved_counts['documents']} to 'documents', "
            f"{moved_counts['media']} to 'media', and {moved_counts['others']} to 'others'.")

organized_files = organize_files_in_folder("/Users/greatmaster/Desktop/projects/oreilly-live-trainings/oreilly-python-course/notebooks/assets")

print(organized_files)