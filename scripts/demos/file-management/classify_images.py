#!/usr/bin/env -S uv run -s
# /// script
# requires-python = ">=3.9"
# dependencies = ["ollama"]
# ///

"""Classify images into category folders using a local vision model (Ollama).

Automation category: File management + AI (local, no API key).

Input   -> a folder of images and a list of categories
Process -> show each image to the gemma4 vision model and ask which category it fits
Output  -> images moved (or copied with --copy) into one subfolder per category

Run it like:
    # move files (default):
    uv run scripts/demos/file-management/classify_images.py /path/to/images \
        --categories Screenshots Photos Documents Receipts Other

    # copy instead of move, into a custom output directory:
    uv run scripts/demos/file-management/classify_images.py /path/to/images \
        --categories Screenshots Photos --copy --output /path/to/organized-images

Needs: `ollama` running locally with the `gemma4` model pulled (`ollama pull gemma4`).
       No API key. Images it can't classify are placed in an "Uncategorized" folder.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import ollama


SUPPORTED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tif", ".tiff", ".heic"
}


def _iter_images(folder_path: Path) -> Iterable[Path]:
    for path in folder_path.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def _short_file_hash(path: Path, length: int = 8) -> str:
    md5 = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()[:length]


def _classify_with_ollama(image_path: Path, categories: List[str]) -> str:
    # Prompt asks the model to return ONLY the category name
    prompt = (
        f"Classify this image according to these categories: {categories}. "
        "Your output should ONLY be the category name and nothing else."
    )
    try:
        # gemma4 is a multimodal model: the image is attached via `images=[...]`
        # so the model actually sees the picture (not just its file path).
        response = ollama.chat(
            model="gemma4",
            messages=[
                {"role": "user", "content": prompt, "images": [str(image_path)]}
            ],
        )
        raw = (response["message"]["content"] or "").strip()
        # Use the last non-empty line, stripped of extra punctuation/quotes
        candidate = "\n".join([line for line in raw.splitlines() if line.strip()]).splitlines()[-1].strip()
        candidate = candidate.strip("`\"' .:;!#[]{}()\t")
        # Normalize to one of the provided categories; case-insensitive exact match
        lower_to_original = {c.lower(): c for c in categories}
        if candidate.lower() in lower_to_original:
            return lower_to_original[candidate.lower()]
        # Try contains match (e.g., "Category: Photos")
        for c in categories:
            if c.lower() in candidate.lower():
                return c
        return "Uncategorized"
    except Exception:
        return "Uncategorized"


def _prepare_destination(base: Path, category: str, source_file: Path) -> Path:
    category_dir = base / category
    category_dir.mkdir(parents=True, exist_ok=True)
    destination = category_dir / source_file.name
    if destination.exists():
        suffix = source_file.suffix
        stem = source_file.stem
        digest = _short_file_hash(source_file)
        destination = category_dir / f"{stem}_{digest}{suffix}"
    return destination


def _move_or_copy(src: Path, dst: Path, copy: bool) -> None:
    if copy:
        shutil.copy2(src, dst)
    else:
        shutil.move(str(src), str(dst))


def organize_images_in_folder(
    folder_path: str,
    categories: Iterable[str],
    output_path: str = "./organized-images",
    copy_instead_of_move: bool = False,
) -> Dict[str, object]:
    folder = Path(folder_path).expanduser().resolve()
    output = Path(output_path).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)

    category_list = list(categories)
    if not category_list:
        category_list = ["Screenshots", "Photos", "Documents", "Receipts", "Other"]

    summary = {
        "processed": 0,
        "moved": 0,
        "copied": 0,
        "errors": 0,
        "uncategorized": 0,
        "by_category": {c: 0 for c in category_list},
        "mappings": [],  # list of (src, dst, category)
    }

    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"Folder not found or not a directory: {folder}")

    for image_path in _iter_images(folder):
        summary["processed"] += 1
        category = _classify_with_ollama(image_path, category_list)
        if category not in category_list:
            summary["uncategorized"] += 1
        destination = _prepare_destination(output, category, image_path)
        try:
            _move_or_copy(image_path, destination, copy_instead_of_move)
            summary["mappings"].append((str(image_path), str(destination), category))
            if copy_instead_of_move:
                summary["copied"] += 1
            else:
                summary["moved"] += 1
            if category in summary["by_category"]:
                summary["by_category"][category] += 1
            else:
                summary["by_category"][category] = 1
        except Exception:
            summary["errors"] += 1

    _print_report(summary, output, copy_instead_of_move)
    return summary


def _print_report(summary: Dict[str, object], output_dir: Path, copied: bool) -> None:
    action_emoji = "📄➡️" if copied else "📦➡️"
    action_word = "copied" if copied else "moved"

    print("\n" + "═" * 60)
    print("🗂️  Image Organizer Report")
    print("═" * 60)
    print(f"📍 Output directory: {output_dir}")
    print(
        f"📊 Processed: {summary['processed']}  |  ✅ {action_word.title()}: {summary[action_word]}  |  ⚠️ Errors: {summary['errors']}  |  🏷️ Uncategorized: {summary['uncategorized']}"
    )

    if summary.get("by_category"):
        print("\n📁 By category:")
        for category, count in sorted(summary["by_category"].items(), key=lambda x: (-x[1], x[0])):
            if count > 0:
                print(f"  - 🏷️ {category}: {count}")

    # Show up to 10 mappings for quick reference
    mappings: List[Tuple[str, str, str]] = summary.get("mappings", [])  # type: ignore[assignment]
    if mappings:
        print("\n" + ("🗺️  Mappings (first 10):"))
        for src, dst, category in mappings[:10]:
            print(f"  {action_emoji} [{category}] {Path(src).name} → {dst}")

    print("\n✨ Done.")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Organize images in a folder using Ollama classification.")
    parser.add_argument("folder", help="Path to the folder containing images")
    parser.add_argument(
        "--categories",
        "-c",
        nargs="+",
        default=[],
        help="List of categories to use for classification (space-separated)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="./organized-images",
        help="Destination base folder (default: ./organized-images)",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy files instead of moving (default is to move)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    organize_images_in_folder(
        folder_path=args.folder,
        categories=args.categories,
        output_path=args.output,
        copy_instead_of_move=args.copy,
    )