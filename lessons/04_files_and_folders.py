# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
LESSON 04 — Files and folders (the real ones)
=============================================

So far we practiced on pretend filenames. Today the script touches YOUR
actual disk — strictly READ-ONLY. It looks, it counts, it reads. The
only thing it writes is one tiny note in your computer's scratch space.

This is also your first "blast radius" lesson: before running ANY
AI-generated script, you ask "what does this touch?" This one touches:
your home folder (look only), one repo file (read only), one temp file
(write). That's the whole radius.

After this lesson you can READ:  import  ·  pathlib.Path  ·  iterdir()  ·  .suffix / .name  ·  read_text / write_text

Run me with:
    uv run lessons/04_files_and_folders.py
"""

# 🗣 EXPLAIN IT (before running): in one sentence — what is this script FOR?

# ── import: borrowing tools ──────────────────────────────────────────────
# import pulls a toolbox into the script. Why you care: the imports at
# the top of an AI script are its ingredient list — read them FIRST to
# see what the script CAN touch (disk? internet? email?). More in lesson 05.

from pathlib import Path   # the standard toolbox for files and folders
import tempfile            # the standard toolbox for scratch space

# ── Path: an address on your disk ────────────────────────────────────────
# Path.home() is your user folder; the / operator glues addresses together.

home = Path.home()

# ── PREDICT: what will this print on YOUR machine? ──
print(f"Your home folder is: {home}")

downloads = home / "Downloads"          # gluing: /Users/you + Downloads
print(f"Your Downloads would be at: {downloads}")

# .exists() asks the disk a True/False question (lesson 03 vocabulary!).
if downloads.exists():
    # ── iterdir(): the real version of our pretend list ──────────────────
    # It yields every item in a folder — a loopable list of Paths.
    # LOOK, don't touch: counting and printing changes nothing on disk.
    # (Names starting with "." are hidden system files — we leave those out.)
    files = [item for item in downloads.iterdir()
             if item.is_file() and not item.name.startswith(".")]
    print(f"Downloads currently holds {len(files)} files. (Just looking!)")

    print("A peek at the first few:")
    for item in files[:5]:                       # [:5] = only the first 5
        # .name is the filename; .suffix is the extension, dot included.
        # This replaces lesson 02's split(".") trick — it's the tool
        # AI scripts actually use.
        print(f"  {item.name}   (type: {item.suffix or 'no extension'})")
else:
    print("No Downloads folder found here — no problem, the lesson goes on.")

# ── reading a file: read_text() ──────────────────────────────────────────
# One call, whole file, as a string. Read-only — the file is unchanged.
readme = Path(__file__).parent.parent / "README.md"
# ^ __file__ is THIS script's address; .parent steps up one folder.
#   So: this file -> lessons/ -> the repo root, where README.md lives.

if readme.exists():
    first_line = readme.read_text().splitlines()[0]
    # ── PREDICT: what's the first line of this repo's README? ──
    print(f'\nFirst line of the README: "{first_line}"')

# ── recognition only: the other way scripts open files ───────────────────
# AI code often reads files with a "with" block instead of read_text():
#
#     with open("notes.txt") as f:
#         text = f.read()
#
# The with-block GUARANTEES the file gets closed properly, even if
# something breaks midway through. Same result as read_text() — and when
# AI code opens files this way, that's a good sign: it's the careful form.

# ── writing a file: write_text() ─────────────────────────────────────────
# Writing is the moment a script STARTS having a blast radius. We aim
# ours at the system scratch folder, where files are temporary by design.

scratch = Path(tempfile.mkdtemp(prefix="lesson04_"))   # a fresh temp folder
note = scratch / "note_to_self.txt"

note.write_text("Files hold text. Python reads and writes it. That's automation fuel.\n")

# ── PREDICT: will the read-back match what we wrote? ──
print(f"\nWrote a note to: {note}")
print(f'It says: "{note.read_text().strip()}"')

print("\nRead, count, peek, one careful write. Your disk is exactly as it was —")
print("plus one throwaway note. Next lesson: where packages come from.")

# ✏️ TRY IT:
#   1. Change downloads to  home / "Desktop"  and run — how many files
#      live there?
#   2. Change files[:5] to files[:10] to peek at more names.
#   3. Edit the note's text, run again, and open the printed file path
#      in any text editor to see your words on disk.
