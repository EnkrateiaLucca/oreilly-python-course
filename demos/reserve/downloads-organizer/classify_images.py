# /// script
# requires-python = ">=3.12"
# dependencies = ["ollama"]
# ///
"""Sort images into folders by CONTENT, using a local vision model (Ollama).

The organizer sorts by extension; this variant actually LOOKS at each picture.
Everything runs on your machine — no API key, nothing leaves your laptop.

Input   -> a folder of images + a list of category names
Process -> show each image to the local gemma4 vision model, ask which category fits
Output  -> images moved into one subfolder per category (Uncategorized if unsure)

Safe by default: it only PREVIEWS the moves. Pass --apply to actually move files.

Run it like:
    uv run demos/reserve/downloads-organizer/classify_images.py practice-mess
    uv run demos/reserve/downloads-organizer/classify_images.py practice-mess --apply

Needs: Ollama running locally with the model pulled once:  ollama pull gemma4
"""

import argparse
import shutil
import sys
from pathlib import Path

import ollama

MODEL = "gemma4"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}


def require_ollama() -> None:
    """Fail with a friendly fix message if Ollama isn't reachable."""
    try:
        ollama.list()
    except Exception:
        print("Could not reach Ollama on this machine.")
        print("1) Install it from https://ollama.com and start the app")
        print(f"2) Pull the model once with:  ollama pull {MODEL}")
        sys.exit(1)


def classify(image: Path, categories: list[str]) -> str:
    """Ask the local vision model which category this image belongs to."""
    prompt = (f"Classify this image into exactly one of these categories: "
              f"{', '.join(categories)}. Reply with ONLY the category name.")
    try:
        # The image is attached via images=[...], so the model actually SEES the
        # pixels — it is not just reading the filename.
        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt, "images": [str(image)]}],
        )
        answer = (response["message"]["content"] or "").strip().strip("`\"'.:; ")
    except Exception:
        return "Uncategorized"

    # Normalize the reply back to one of OUR category names (models improvise).
    for category in categories:
        if category.lower() in answer.lower():
            return category
    return "Uncategorized"


def sort_images(folder: Path, categories: list[str], apply: bool) -> None:
    images = [f for f in sorted(folder.iterdir())
              if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS]
    if not images:
        print(f"No images found directly inside {folder}/ — nothing to do.")
        return

    for image in images:
        category = classify(image, categories)
        if apply:
            destination = folder / category
            destination.mkdir(exist_ok=True)
            shutil.move(str(image), str(destination / image.name))
            print(f"moved       {image.name}  ->  {category}/")
        else:
            print(f"would move  {image.name}  ->  {category}/")

    if not apply:
        print("\nThis was a DRY RUN — nothing moved. Re-run with --apply to move files.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sort images into folders using local AI vision.")
    parser.add_argument("folder", help="Folder containing the images, e.g. practice-mess")
    parser.add_argument("--categories", nargs="+",
                        default=["Screenshots", "Photos", "Receipts"],
                        help="Category names (default: Screenshots Photos Receipts)")
    parser.add_argument("--apply", action="store_true",
                        help="Actually move files (default: preview only)")
    args = parser.parse_args()

    folder = Path(args.folder).expanduser()
    if not folder.is_dir():
        print(f"That folder does not exist: {folder}")
        sys.exit(1)

    require_ollama()
    sort_images(folder, args.categories, apply=args.apply)


if __name__ == "__main__":
    main()
