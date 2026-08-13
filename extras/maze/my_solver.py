"""YOUR maze-solving code. This is the only file you edit.

The robot starts top-left, the flag ⚑ is bottom-right.
Compass moves: N = up · S = down · E = right · W = left

Run me with:   uv run play.py            (level 1 — the robot follows MOVES)
               uv run play.py --level 2  (level 2 — the robot asks next_move)
               uv run play.py --level 3  (level 3 — 5 random mazes)
"""

# ═══════════════════════════════════════════════════════════════════
# LEVEL 1 — beat THIS maze with a plan.
#
# Your "code" is just a string of moves. Watch the robot follow it,
# see where it goes wrong, fix the plan, run again. (Congratulations —
# that edit → run → watch loop is what programming *is*.)
# Spaces are allowed, so you can chunk it: "SS EE SS"
# ═══════════════════════════════════════════════════════════════════

MOVES = "SSEE"   # ← start here. Run it. Watch. Extend.


# ═══════════════════════════════════════════════════════════════════
# LEVEL 2 — beat this maze with LOGIC instead of a hand-made plan.
#
# The robot calls your function before every step and shows you around:
#
#   view["walls"]     {"N": True, "S": False, ...}   True = wall (blocked)
#   view["facing"]    the direction of your last successful step, e.g. "E"
#   view["position"]  (row, col) where you are
#   view["exit"]      (row, col) of the flag
#   view["memory"]    a dict that survives between steps — scribble in it
#
# Return one letter: "N", "S", "E" or "W".
#
# 💡 THE CLASSIC TRICK — "right hand on the wall":
#    walk the maze keeping your right hand touching the wall and you
#    will always find the exit. As code, in the order you should try:
#      1) the direction to the RIGHT of where you're facing
#      2) straight ahead
#      3) to the LEFT
#      4) behind you (dead end — turn around)
#    ...and take the FIRST one that has no wall.
#    These two lookup tables do the compass math for you:
# ═══════════════════════════════════════════════════════════════════

RIGHT_OF = {"N": "E", "E": "S", "S": "W", "W": "N"}
LEFT_OF  = {"N": "W", "W": "S", "S": "E", "E": "N"}


def next_move(view):
    # This starter is deliberately terrible: it only ever goes east.
    # Run level 2, watch it bonk into a wall forever, then make it smart.
    return "E"

    # ✏️ TRY IT, in stages:
    #   1. Make it go east only when east is open, otherwise south.
    #      (An if/else — better! But it still gets stuck in some corners.)
    #   2. Build the right-hand rule from the recipe above: a list of the
    #      four directions in try-order, a loop over them, an if inside.
    #      ~6 lines. It beats level 2 — and all five mazes in level 3.
