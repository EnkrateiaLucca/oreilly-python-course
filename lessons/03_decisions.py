# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
LESSON 03 — Decisions and functions
===================================

A file organizer has one decision at its heart: "this file's name ends
in .pdf, so it belongs in Documents." Today we read the two tools that
express that: if/elif/else (the decision) and functions (a named recipe
you can reuse).

After this lesson you can READ:  True/False checks  ·  if / elif / else  ·  def (functions)  ·  return

Run me with:
    uv run lessons/03_decisions.py
"""

# 🗣 EXPLAIN IT (before running): in one sentence — what is this script FOR?

# ── yes/no questions: True and False ─────────────────────────────────────
# .endswith(...) asks a question about text and answers True or False.
# Why you care: every "should this script do X?" moment in AI-generated
# code boils down to one of these True/False checks — find the check,
# and you know when the action fires.

filename = "tax_return_2025.pdf"

# ── PREDICT: True or False, for each line? ──
print(filename.endswith(".pdf"))
print(filename.endswith(".jpg"))

# ── if / elif / else: the fork in the road ───────────────────────────────
# Read top to bottom; the FIRST true branch wins, the rest are skipped.
# else is the catch-all when nothing matched.

size_mb = 850

# ── PREDICT: which ONE of these three lines will print? ──
if size_mb > 1000:
    print("Huge file — probably a video or an installer.")
elif size_mb > 100:
    print("Big file — worth a look before keeping.")
else:
    print("Small file — no worries.")

# ── functions: name a recipe once, use it forever ────────────────────────
# def gives a block of steps a name; return hands the answer back.
# Why you care: AI writes scripts as a stack of small functions. Reading
# a script = reading each def's name, inputs, and return — the function
# names ARE the table of contents.

def folder_for(filename):
    """Decide which folder a downloaded file belongs in."""
    name = filename.lower()   # so "PHOTO.JPG" and "photo.jpg" match alike

    if name.endswith((".jpg", ".jpeg", ".png", ".heic")):
        return "Images"
    elif name.endswith((".pdf", ".docx", ".txt")):
        return "Documents"
    elif name.endswith((".mp3", ".wav")):
        return "Music"
    elif name.endswith((".mp4", ".mov")):
        return "Videos"
    else:
        return "Other"        # the safety net for anything unexpected

# Call the recipe: write its name, hand it an input in parentheses.

# ── PREDICT: what folder comes back for each of these? ──
# (Careful with the third one — reread the first line of folder_for.)
print(folder_for("vacation.jpg"))
print(folder_for("invoice_march.pdf"))
print(folder_for("SCREENSHOT.PNG"))
print(folder_for("mystery_download"))

# Now combine with lesson 02: loop the decision over a whole folder.
downloads = ["vacation.jpg", "tax_return_2025.pdf", "song.mp3",
             "screenshot.png", "install_me.dmg"]

print()
print("The organizer's plan (nothing is moved — it's just talk so far):")
for filename in downloads:
    print(f"  {filename}  ->  {folder_for(filename)}/")

print()
print("That loop-plus-function IS the brain of lesson 09's organizer.")
print("Next lesson: touching the real disk (gently, read-only).")

# ✏️ TRY IT:
#   1. Teach folder_for about spreadsheets: add ".xlsx" and ".csv" so
#      they return "Spreadsheets". Then add "budget.xlsx" to downloads.
#   2. Change size_mb to 42, predict which branch wins, then run.
#   3. Delete the .lower() line and run again — what happens to
#      "SCREENSHOT.PNG"? (This exact bug ships in real AI scripts.
#      Now you can spot it.)
