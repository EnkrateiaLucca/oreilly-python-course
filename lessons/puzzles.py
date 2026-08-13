# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
PUZZLES — rebuild the script (a.k.a. Parsons puzzles)
=====================================================

Three tiny scripts you already know how to READ (lessons 02-04) — but
their lines arrived shuffled. Your job: type the numbers in the order
that rebuilds each script. No writing code, just arranging it.

Indentation is shown explicitly: each ···· marks one level (4 spaces).
An indented line always belongs to the unindented line above it.

Run me with:
    uv run lessons/puzzles.py
"""

import sys

PUZZLES = [
    {
        "story": "a loop that counts the PDFs in a list, then announces the total",
        "solution": [
            'count = 0',
            'for name in ["report.pdf", "photo.jpg", "invoice.pdf"]:',
            '    if name.endswith(".pdf"):',
            '        count = count + 1',
            'print(f"Found {count} PDF(s)")',
        ],
        "display": [2, 4, 0, 3, 1],
        "hint": ('the tally box must exist BEFORE the loop adds to it — '
                 'so "count = 0" comes first.'),
    },
    {
        "story": "an if/elif router: .pdf files to Documents/, .jpg to Images/, the rest to Other/",
        "solution": [
            'name = "invoice_march.pdf"',
            'if name.endswith(".pdf"):',
            '    print("-> Documents/")',
            'elif name.endswith(".jpg"):',
            '    print("-> Images/")',
            'else:',
            '    print("-> Other/")',
        ],
        "display": [3, 0, 6, 2, 5, 1, 4],
        "hint": ('a router needs something to route — the "name = ..." line comes '
                 'first. Then the fork reads if -> elif -> else, top to bottom, '
                 'each branch trailed by its indented print.'),
    },
    {
        "story": "a function + loop that renames messy files (print-only — nothing really moves)",
        "solution": [
            'def tidy(name):',
            '    return name.lower().replace(" ", "_")',
            'files = ["My Resume.PDF", "Beach Photo.JPG"]',
            'for name in files:',
            '    print(f"{name}  ->  {tidy(name)}")',
        ],
        "display": [4, 1, 3, 0, 2],
        "hint": ('scripts define their tools before using them — "def tidy(name):" '
                 'comes first, with its indented return right underneath.'),
    },
]


def ask(prompt):
    """input(), but with a graceful exit if the input stream runs dry."""
    try:
        return input(prompt)
    except EOFError:
        print("\nInput ended early — come back and finish anytime!")
        sys.exit(0)


def with_visible_indent(line):
    """Show leading 4-space groups as ···· so indentation is unmissable."""
    stripped = line.lstrip(" ")
    depth = (len(line) - len(stripped)) // 4
    return "····" * depth + stripped


def play(number, puzzle):
    shown = [puzzle["solution"][i] for i in puzzle["display"]]
    # The right answer, in shown-numbers: where each solution line ended up.
    answer = [puzzle["display"].index(i) + 1 for i in range(len(shown))]

    print(f"\n── Puzzle {number}: {puzzle['story']} ──")
    print("The shuffled lines (···· = one indent level):\n")
    for position, line in enumerate(shown, start=1):
        print(f"  {position} |  {with_visible_indent(line)}")

    example = " ".join(str(n) for n in range(len(shown), 0, -1))
    wrong_tries = 0
    while True:
        raw = ask(f"\nYour order (e.g. {example}): ")
        tokens = raw.replace(",", " ").split()
        valid = sorted(tokens) == sorted(str(n + 1) for n in range(len(shown)))
        if not valid:
            print(f"  I need the numbers 1-{len(shown)}, each exactly once — try again.")
            continue

        if [int(t) for t in tokens] == answer:
            print("\n  Yes! Assembled, it reads:\n")
            break
        wrong_tries += 1
        if wrong_tries == 1:
            print(f"  Not quite. Hint: {puzzle['hint']}")
            print("  Have another go!")
        else:
            correct = " ".join(str(n) for n in answer)
            print(f"\n  No worries — the order is {correct}. Assembled, it reads:\n")
            break

    for line in puzzle["solution"]:
        print(f"      {line}")
    return wrong_tries == 0


print("Three shuffled scripts. Rebuild each by typing the line numbers in order.")

first_try_wins = 0
for number, puzzle in enumerate(PUZZLES, start=1):
    if play(number, puzzle):
        first_try_wins += 1

print(f"\nDone — {first_try_wins} of {len(PUZZLES)} solved on the first try.")
print("Reordering forces you to see the SKELETON: setup → loop → decision → output.")
print("That skeleton is in every AI script you'll ever audit. Spot it, and")
print("the wall of code becomes a floor plan.")

# ✏️ TRY IT:
#   1. Rerun and solve all three from memory — faster this time?
#   2. Open lessons/02_lists_and_loops.py and find the same skeleton:
#      setup (the list) → loop → decision → output.
#   3. Ask an AI for a 5-line script that counts .jpg files, shuffle the
#      lines on paper, and hand it to a colleague. You just MADE a puzzle.
