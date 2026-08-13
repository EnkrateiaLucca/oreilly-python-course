# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
LESSON 01 — First run
=====================

Welcome! You are looking at a Python *script*: a plain text file your
computer performs top to bottom, like a recipe.

Quick promise about this course: you will NOT learn to write code from
scratch. AI writes the scripts. YOUR job is to READ them, RUN them
safely, and STEER them — and by lesson 09 you'll read every line of a
script that cleans up a messy Downloads folder.

After this lesson you can READ:  print()  ·  variables  ·  f-strings

Run me from the repo folder with:
    uv run lessons/01_first_run.py
"""

# ── print(): the script talking back to you ──────────────────────────────
# Why you care: AI-generated scripts narrate what they're doing with
# print() lines — if you can read those, you can follow the whole story.

print("Hello! If you can read this, your setup works.")
print("That was the hard part. Everything else is just reading.")

# ── variables: labelled boxes ────────────────────────────────────────────
# A variable is a labelled box holding a value. The label goes on the
# left of the = sign, the value goes on the right.
# Why you care: when AI writes a script for you, the variables near the
# top (folder names, limits, email addresses) are the KNOBS you're
# allowed to turn without understanding anything else.

folder_name = "Downloads"      # text goes in quotes — this is a "string"
files_inside = 47              # numbers don't need quotes
biggest_file_mb = 3.2          # decimals are fine too

# ── PREDICT: what will this print? ──
# (Hint: print shows the VALUE in the box, not the label on the box.)
print(folder_name)
print(files_inside)

# A box can be relabelled — the old value is simply replaced.
files_inside = 51   # ...four new downloads arrived

# ── PREDICT: what will this print? 47 or 51? ──
print(files_inside)

# ── f-strings: fill-in-the-blank sentences ───────────────────────────────
# Put an f before the quotes, then drop any variable into {curly braces}.
# Why you care: every status message an AI script prints — "Moved 12
# files to Documents" — is an f-string. Read the braces, know the knobs.

print(f"Your {folder_name} folder has {files_inside} files.")

# The braces can hold small calculations too, not just variables.

# ── PREDICT: what number appears in this sentence? ──
print(f"If you deleted 10 files, {files_inside - 10} would remain.")

# One last trick: {value:.1f} means "show 1 digit after the decimal".
print(f"The biggest file is {biggest_file_mb:.1f} MB. Nothing scary here.")

print()
print("Done! You just READ and RAN a Python script. Lesson 02 awaits.")

# ✏️ TRY IT: (edit this file, save, and run it again)
#   1. Change folder_name to "Desktop" and run — which lines change?
#   2. Add a line at the bottom:  print(f"There are {files_inside * 2} files on my backup drive.")
#   3. Break it on purpose: remove the f before one of the f-strings.
#      Run it, read the output — Python prints the braces literally.
#      Now you know what a *missing* f looks like in an AI's script.
