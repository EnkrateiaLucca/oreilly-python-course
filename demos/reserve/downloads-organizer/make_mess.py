# /// script
# requires-python = ">=3.12"
# ///
"""Create a fake messy folder so you can practice organizing WITHOUT touching real files.

This is your sandbox builder. It fills `practice-mess/` with the kind of junk that
piles up in a real Downloads folder: text notes, CSVs, "PDFs", and a few real PNG
images. Practice here first — never on your actual Downloads.

Run it like:
    uv run demos/reserve/downloads-organizer/make_mess.py           # preview
    uv run demos/reserve/downloads-organizer/make_mess.py --apply   # actually create

Needs: nothing (no API key, standard library only).
"""

import argparse
import struct
import sys
import zlib
from pathlib import Path


def solid_png(width: int, height: int, rgb: tuple[int, int, int]) -> bytes:
    """Build a tiny but REAL PNG image of one solid color, using only the stdlib.

    A PNG is just a signature followed by length-tagged 'chunks' — this is what a
    file format looks like under the hood. The result opens in any image viewer.
    """
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data)))

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    row = b"\x00" + bytes(rgb) * width          # each row starts with a filter byte
    pixels = zlib.compress(row * height)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
            + chunk(b"IDAT", pixels) + chunk(b"IEND", b""))


# filename -> file contents (bytes). A realistic slice of Downloads-folder chaos.
MESS: dict[str, bytes] = {
    "meeting-notes.txt": b"Standup notes: ship the report by Friday.\n",
    "old-todo.md": b"- [ ] cancel unused subscriptions\n- [ ] file expenses\n",
    "random-thoughts.txt": b"idea: automate the boring parts first\n",
    "invoice-2026-03.pdf": b"%PDF-1.4\n% fake practice invoice, safe to move around\n",
    "ebook-sample.pdf": b"%PDF-1.4\n% fake practice ebook, safe to move around\n",
    "expenses-q1.csv": b"date,amount\n2026-01-05,42.50\n2026-02-11,99.00\n",
    "contacts-export.csv": b"name,email\nAda,ada@example.com\n",
    "budget-draft.xlsx": b"fake spreadsheet bytes for practice\n",
    "installer-notes.log": b"nothing installed, just a leftover log file\n",
    "screenshot-2026-01-03.png": solid_png(32, 32, (90, 90, 95)),
    "photo-beach.png": solid_png(32, 32, (30, 120, 220)),
    "receipt-scan.png": solid_png(32, 32, (245, 245, 240)),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a practice mess folder to organize.")
    parser.add_argument("--target", default="practice-mess",
                        help="Folder to create the mess in (default: ./practice-mess)")
    parser.add_argument("--apply", action="store_true",
                        help="Actually create the files (default: preview only)")
    args = parser.parse_args()

    target = Path(args.target).expanduser()

    for name in MESS:
        if args.apply:
            print(f"created      {target / name}")
        else:
            print(f"would create {target / name}")

    if not args.apply:
        print(f"\nDry run: nothing written. Re-run with --apply to create "
              f"{len(MESS)} practice files in {target}/")
        return

    target.mkdir(parents=True, exist_ok=True)
    for name, content in MESS.items():
        (target / name).write_bytes(content)
    print(f"\nDone. Now try:  uv run demos/reserve/downloads-organizer/organize.py {target}")


if __name__ == "__main__":
    try:
        main()
    except OSError as error:
        print(f"Could not create the practice folder: {error}")
        sys.exit(1)
