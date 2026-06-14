# /// script
# requires-python = ">=3.12"
# ///

import argparse
import shutil
from pathlib import Path

def organize_files_in_folder(folder_path, apply=False):
    """
    Organize files in the given folder into three subfolders:
    - documents: .md, .txt, .pdf
    - media: .png, .jpg, .jpeg, .gif, .bmp, .tiff, .svg, .webp
    - others: any other file types or files without extension

    Only top-level files in folder_path are moved (subfolders are left intact).
    If a filename conflict occurs in the destination folder, a numeric suffix is added.
    By default this is a dry run that only reports what would move; pass apply=True
    to actually move the files. Returns a summary message with counts.
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

    if apply:
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

        # Move the file (or just report it in dry-run mode)
        if apply:
            try:
                shutil.move(str(entry), str(dest_path))
                moved_counts[key] += 1
            except Exception as e:
                # If a file couldn't be moved, continue with others
                print(f"Warning: could not move '{entry.name}': {e}")
        else:
            moved_counts[key] += 1
            print(f"Would move '{entry.name}' -> {key}/")

    verb = "Moved" if apply else "Would move"
    return (f"{verb} {moved_counts['documents']} file(s) to 'documents', "
            f"{moved_counts['media']} to 'media', and {moved_counts['others']} to 'others'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sort the top-level files of a folder into documents/ media/ others/."
    )
    parser.add_argument("folder", help="Folder to organize")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually move the files (default is a dry run that only reports)",
    )
    args = parser.parse_args()

    print(organize_files_in_folder(args.folder, apply=args.apply))
    if not args.apply:
        print("\nDry run only - re-run with --apply to actually move the files.")