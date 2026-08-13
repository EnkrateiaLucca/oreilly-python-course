# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
LESSON 06 — When it breaks (reading the wreckage)
=================================================

Every script — yours, AI's, anybody's — eventually fails. That's not a
disaster; it's a MESSAGE. Python leaves a note called a *traceback*
saying exactly what went wrong and where. Most people see a wall of
scary text; you're about to learn the 10-second reading trick.

This script breaks ON PURPOSE, twice, and keeps going both times — so
you can practice reading crashes in perfect safety.

After this you can read:  a traceback  ·  try/except  ·  and the three
red-flag lines that mean STOP before running AI code.

Run me with:
    uv run lessons/06_when_it_breaks.py
"""

# 🗣 EXPLAIN IT (before running): in one sentence — what is this script FOR?

import traceback              # stdlib toolbox for capturing crash reports
from pathlib import Path      # lesson 04's file toolbox

# ── Part 1: tracebacks — the crash report ────────────────────────────────
# Why you care: when an AI script dies, the traceback is what you read —
# and what you paste back to the AI. Reading it first, even roughly,
# keeps you steering instead of copy-pasting blind.

folders = {"pdf": "Documents", "jpg": "Images", "mp3": "Music"}

# ── PREDICT: this next line asks for a key that isn't there — will
#    Python guess a folder, or give up? ──
try:
    destination = folders["png"]          # <- the crash happens HERE
except KeyError:
    print("CRASH #1 — the note Python left behind:\n")
    print(traceback.format_exc())

# The reading trick (works on EVERY traceback, however long):
#   1. Read the LAST line FIRST:   KeyError: 'png'
#      That's the exception TYPE (what kind of problem) plus the message
#      (which thing, exactly). Nine times out of ten, that's all you need.
#   2. Then scan up for the line number in YOUR file
#      (06_when_it_breaks.py) — that's where to look in the code.
#   3. Ignore anything from site-packages or deep library internals:
#      that's the machinery, not your problem.
print("Reading order: LAST line first (KeyError: 'png'), then the line")
print("number in YOUR file, and skip the library noise. That's the trick.\n")

# ── PREDICT: this path exists on no computer anywhere. What TYPE will
#    the last line of the traceback show this time? ──
try:
    Path("/definitely/not/a/real/folder/notes.txt").read_text()
except FileNotFoundError:
    print("CRASH #2 — different problem, same reading order:\n")
    print(traceback.format_exc())

print("Last line first: FileNotFoundError, plus the exact path it wanted.")
print("New error, same 10-second diagnosis.\n")

# ── Part 2: try/except — the script's safety net ─────────────────────────
# You just watched it work twice: try means "attempt this", except means
# "if THAT problem happens, do this instead of dying". Here's the same
# doomed lookup from CRASH #1, netted properly with a plan B:

wanted = "png"
try:
    destination = folders[wanted]
    print(f".{wanted} files go to {destination}/")
except KeyError:
    print(f"No rule for .{wanted} yet — filing it under Other/ instead.")
    destination = "Other"                 # plan B: a sensible fallback

# ── PREDICT: same missing key as CRASH #1 — why no traceback this time? ──
print(f"Still running fine, and destination = {destination!r}.\n")

# Why you care: when you audit AI code that talks to the internet or to
# files, LOOK FOR THE NET around the risky lines — and notice when it's
# MISSING. A netless requests.get() is one bad Wi-Fi moment away from a
# face-plant; now you know to ask the AI to add the net.

# ── Part 3: the three red-flag lines (we READ these, never RUN them) ─────
# Some lines deserve a full stop before you run any script containing
# them. Not because they're evil — because of what they CAN do. They are
# printed below as plain text; this script never executes any of them.

RED_FLAGS = [
    ('subprocess.run([...])', "runs ANY other program on your computer"),
    ('os.system("...")',      "same power, older style — still any program"),
    ('eval(...) / exec(...)', "runs TEXT as if it were Python code"),
]

print("The three red-flag lines to stop on in AI-generated code:")
for flag, power in RED_FLAGS:
    print(f"  {flag:<24} — {power}")

print()
print("Seeing one of these is NOT proof of a bad script — plenty of honest")
print("automation shells out. It means STOP and ask the Run Gate question:")
print('"what EXACTLY gets executed here, and where does that text come from?"')
print("If you can't answer it, don't run it — ask the AI to explain or rewrite.")

# A tiny audit drill. One of these six printed lines is a red flag —
# your job (TRY IT #3) is to spot it:
SNIPPET = '''\
    from pathlib import Path
    import os

    for file in Path("Downloads").iterdir():
        if file.suffix == ".zip":
            os.system(f"unzip {file}")'''

print()
print("Audit drill — one line below deserves a full stop. Which one?")
print(SNIPPET)

print()
print("Crashes are messages, nets are manners, red flags are stop signs.")
print("Next lesson: the internet as an ingredient — a real API, safely netted.")

# ✏️ TRY IT:
#   1. In the CRASH #1 line, change "png" to "gif" and rerun — which part
#      of the traceback changed? Now change it to "pdf" (a key that
#      exists) — what happens to CRASH #1 entirely?
#   2. In Part 2, delete the try/except net (keep just the lookup line,
#      unindented). PREDICT: does the script still reach the red-flag
#      section? Run it and read the real traceback you just caused.
#   3. The audit drill: which of the six printed lines is the red flag,
#      and what's the Run Gate question you'd ask about it?
