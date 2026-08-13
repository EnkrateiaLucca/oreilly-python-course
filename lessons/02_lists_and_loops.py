# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
LESSON 02 — Lists and loops
===========================

Our recurring project is a script that tidies a messy Downloads folder.
Before a script can tidy files, it needs to hold MANY filenames at once
(a list) and do something with EACH one (a loop).

Today we practice on a pretend Downloads folder — just names, no real
files are touched. Real files come in lesson 04.

After this lesson you can READ:  lists  ·  indexing  ·  for-loops  ·  a counting dictionary

Run me with:
    uv run lessons/02_lists_and_loops.py
"""

# 🗣 EXPLAIN IT (before running): in one sentence — what is this script FOR?

# ── lists: many values in one box ────────────────────────────────────────
# Square brackets, commas between items. Why you care: every AI script
# that processes "all the files in a folder" or "each row of a
# spreadsheet" holds them in a list first.

downloads = [
    "vacation.jpg",
    "tax_return_2025.pdf",
    "screenshot.png",
    "invoice_march.pdf",
    "song.mp3",
    "receipt_amazon.pdf",
]

# len() answers "how many items?"
# ── PREDICT: what will this print? ──
print(f"The pretend Downloads folder holds {len(downloads)} files.")

# Items are numbered from 0 (yes, zero — the #1 beginner surprise).
# downloads[0] is the first item; downloads[-1] counts from the end.

# ── PREDICT: which two filenames will this print? ──
print(f"First file: {downloads[0]}")
print(f"Last file:  {downloads[-1]}")

# Slicing: brackets with a colon cut out a RANGE instead of one item.
# downloads[:3] means "just the first 3" — and it works on text too.
report_line = "Downloads audit — March 2026 edition, with extra notes"

# ── PREDICT: how many characters will this preview show? ──
print(f"Preview: {report_line[:20]}...")   # [:20] = the first 20 characters

# ── for-loops: do something with EACH item ───────────────────────────────
# Read it aloud: "for each filename in downloads, do the indented lines."
# Why you care: the loop is the engine of every automation — same small
# action, repeated over 6 files or 6,000. Spot the loop, and you've
# found where the script does its real work.

print()
print("Contents:")
for filename in downloads:
    print(f"  - {filename}")   # the indented part runs once PER item

# ── the three string methods AI code uses constantly ─────────────────────
# .strip() trims stray spaces off both ends; .split() cuts one string
# into a list; .join() glues a list back into one string. Spot these
# three and you can read most of the text-handling in any AI script.

messy = "   invoice_april.pdf   "

# ── PREDICT: what does .strip() remove — and from where? ──
print(f"[{messy.strip()}]")               # the brackets reveal the trimmed edges

# ── PREDICT: how many pieces does this split into? ──
print("tax_return_2025.pdf".split("_"))   # the "_" is where the cuts happen

# ── PREDICT: what single string comes out of this join? ──
print(" | ".join(["vacation.jpg", "song.mp3", "receipt.pdf"]))
# ^ read join inside-out: the LIST is the input, the " | " is the glue.

# ── counting things with a dictionary ────────────────────────────────────
# A dictionary is a list with LABELS instead of positions: {"pdf": 3}
# means "the count filed under 'pdf' is 3". Why you care: AI scripts use
# dictionaries for anything labelled — settings, counts, API answers
# (you'll see a real one in lesson 07).

counts = {}   # start with an empty dictionary

for filename in downloads:
    extension = filename.split(".")[-1]         # "vacation.jpg" -> "jpg"
    counts[extension] = counts.get(extension, 0) + 1
    # ^ "look up this extension's count (0 if it's new), add 1, file it back"

print()
print("File types found:")

# ── PREDICT: how many pdfs? does 'jpg' or 'png' appear first? ──
for extension, how_many in counts.items():      # .items() gives label + value pairs
    print(f"  .{extension}: {how_many} file(s)")

# ── recognition only: the list comprehension ─────────────────────────────
# AI loves writing loops this compact way — same machine, smaller box;
# you never need to WRITE one, just recognize it. Both blocks below
# build the exact same list of PDFs:

pdfs = []
for filename in downloads:                # the long way you just read
    if filename.endswith(".pdf"):
        pdfs.append(filename)             # append = add to the end

pdfs_again = [f for f in downloads if f.endswith(".pdf")]   # the short way

# ── PREDICT: same list twice, or different? ──
print()
print(f"Loop version:          {pdfs}")
print(f"Comprehension version: {pdfs_again}")

print()
print("You just read the core of every file-organizer ever written:")
print("a list of names, a loop over them, and a tally. Lesson 03: decisions.")

# ✏️ TRY IT:
#   1. Add "budget.xlsx" and "budget_final.xlsx" to the downloads list.
#      Run it — what happens to the counts?
#   2. Change the loop line to  for filename in downloads[:3]:
#      and run. The [:3] means "just the first 3" — handy when an AI
#      script says "test on a few files first".
#   3. Predict, then check: what does downloads[1] print? (Not the first!)
