# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "rich",
# ]
# ///
"""
LESSON 05 — Packages: the toolboxes scripts borrow
==================================================

Did you notice? The FIRST time you ran this lesson, uv paused for a
second before anything printed. That pause was uv downloading a package
called "rich" — because the header at the very top of this file asked
for it. You just watched a dependency install itself.

After this lesson you can READ:  the PEP 723 header  ·  import (stdlib vs installed)  ·  from ... import ...
...and you'll have the single most important safety habit in this course.

Run me with:
    uv run lessons/05_packages.py
"""

# 🗣 EXPLAIN IT (before running): in one sentence — what is this script FOR?

# ── two kinds of toolboxes ───────────────────────────────────────────────
# 1) The "standard library" ships WITH Python — always there, no install.
#    pathlib (lesson 04), statistics, random are all standard library.
# Why you care: stdlib imports in an AI script are safe and boring;
# it's the OTHER kind you'll learn to double-check below.

import statistics
import random

file_sizes_mb = [1.2, 0.4, 850.0, 3.3, 0.1]   # our pretend Downloads, in MB

# ── PREDICT: what's the mean of those five numbers? (Rough guess!) ──
print(f"Average file size: {statistics.mean(file_sizes_mb):.1f} MB")
print(f"Middle (median) size: {statistics.median(file_sizes_mb):.1f} MB")
# ^ one giant file drags the average way up but barely moves the median —
#   a thing you now know that most spreadsheets users don't.

# ── PREDICT: what will this print? (Trick question...) ──
print(f"Random pick: {random.choice(file_sizes_mb)} MB")
# ^ You CAN'T predict it — that's the point of random. Knowing which
#   lines are unpredictable is part of reading code.

# 2) INSTALLED packages come from the internet — from a warehouse called
#    PyPI (pypi.org), where anyone can publish. "rich" is one of them:

from rich import print as fancy_print   # borrow ONE tool and rename it

fancy_print("[bold green]This green text comes from 'rich' — a package "
            "somebody published to PyPI, installed just for this script.[/bold green]")

# ── the PEP 723 header: the script's shopping list ───────────────────────
# Scroll to the top of this file. Between the  # ///  fences sits:
#       dependencies = [ "rich" ]
# That's PEP 723 "inline metadata": the script DECLARES what it needs,
# and uv fetches it automatically at run time. No setup steps, ever.
# Why you care: when AI hands you a script, this header is its customs
# declaration — the complete list of outside code it will pull in.

# ── ⚠️ THE HALLUCINATED-PACKAGE CHECK (your new habit) ──────────────────
# AI models sometimes invent packages that DON'T EXIST — studies have
# found roughly 20% of AI-suggested package names are made up. Worse:
# scammers register those fake names on PyPI with malicious code inside,
# waiting for someone to install them. This is a real, current attack.
#
# The habit, every single time, BEFORE the first run of an AI script:
#   1. Read the dependencies list in the PEP 723 header.
#   2. For each name, visit:  https://pypi.org/project/<name>/
#   3. Real package: a project page with docs, a history of releases,
#      and (for popular ones) millions of downloads.  rich? Real.
#   4. Page not found, or registered last week with no description?
#      STOP. Don't run it. Ask the AI: "does <name> really exist on
#      PyPI? If not, rewrite using well-known packages only."
#
# Thirty seconds of checking. It's the seatbelt of this whole course.

suspects = ["rich", "requests", "pandas-csv-pro", "auto-excel-magic"]
print("\nWhich of these are real? Check pypi.org/project/<name>/ ...")
for name in suspects:
    print(f"  https://pypi.org/project/{name}/")
print("(Spoiler: the first two are real workhorses. The last two are the")
print(" kind of plausible-sounding names AI invents. Never assume — check.)")

print("\nNext lesson: scripts that BREAK — on purpose — and how to read the")
print("wreckage calmly. ('requests' and the internet arrive in lesson 07.)")

# ✏️ TRY IT:
#   1. Actually open https://pypi.org/project/rich/ in your browser.
#      Note the release history — that's what "real" looks like.
#   2. Add "cowsay" to the dependencies list up top, then add
#      import cowsay  and  cowsay.cow("moo!")  at the bottom. Run it —
#      watch uv install it on the spot. (Yes, it's a real package. Verify!)
#   3. Change [bold green] to [bold red on white] in the fancy_print line.
