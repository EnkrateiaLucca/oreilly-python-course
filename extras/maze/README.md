# The Maze — an optional extra

A visual, animated "instruct a very literal robot" game. Three levels take you
from *a plan* to *a program* — the arc of the whole course in twenty minutes.

**This is a bonus, not part of the course flow.** Nothing in the lessons, demos,
or slides depends on it. Play it whenever you like — before the course as a
taste, between days for fun, or after as a bragging-rights challenge. The
instructor may or may not bring it out live.

It ships in **two forms**:

## ⭐ Maze Lab (browser) — `maze-lab.html`

Just open the file (double-click, or `open maze-lab.html`). Python code editor
on the left, live animated maze on the right — **real Python**, running in the
browser (Pyodide), no setup at all. Level tabs, ▶ Run (⌘⏎), 🤖 demo autopilot,
🎲 new maze, speed slider, confetti on wins, a console that shows students'
`print(...)` lines, and error panels that teach the lesson-06 "read the last
line first" habit. Code persists between visits (localStorage); ↺ resets to the
starter. Needs internet on first load (CDN download, ~10s), cached after.

**Instructor pocket-ace:** ⌥ Alt-click "🎲 new maze" reveals a winning plan for
the current maze.

## Terminal version — `play.py` + `my_solver.py`

Same engine, same seeds, same levels, animated in the terminal — the no-browser
fallback, and the version that matches the course's terminal aesthetic:

**Status: standing extra.** Deliberately kept out of the slides and run-of-show.
If the instructor ever wants to use it live, the pedagogy checklist below covers
what to watch.

## The arc (and why it works)

| Level | Student writes | Concept smuggled in |
|---|---|---|
| **Demo** (`--demo`) | nothing — the computer plays | the hook: "your code will do this by level 3" |
| **1 — beat THIS maze** | `MOVES = "SSEENN…"` — a string | a program is an exact plan; the edit→run→watch loop |
| **2 — beat it with logic** | `next_move(view)` with if/elif | conditions replace hand-planning; reading `view` = reading state |
| **3 — beat ANY maze** | the same function, unchanged rules | *generalization* — the difference between a plan and a program |

Level 3's punchline is the motivator: 6 lines of logic (the right-hand rule) beat
five mazes the student has never seen. That's the "why code at all, when I could
just do it by hand" answer, felt rather than told.

Vocabulary mapping: level 1 = strings (lesson 01-02) · level 2 = if/elif +
functions + dicts (lessons 02-03) · level 3 = loops + generalization. If ever
used live, the natural slot would be Day 1 after lesson 03 — but it stands
alone just fine as homework, a break activity, or a pre-course teaser.

## Running it

```bash
cd extras/maze
uv run play.py --demo        # the hook: autopilot beats the maze
uv run play.py               # level 1: robot follows MOVES from my_solver.py
uv run play.py --level 2     # level 2: robot asks next_move(view) each step
uv run play.py --level 3     # level 3: five random mazes, scoreboard at the end
```

Useful flags: `--speed slow|normal|fast` · `--seed N` (different layout) ·
`--size 8x12` · `--cheat` (prints a winning MOVES plan — instructor pocket-ace) ·
`--no-anim` (result only).

Everything fails friendly: plan runs out → "ran out at (r,c), extend and rerun";
bad return value → one-line fix message; lost robot → the wall-following hint.
Wall bumps don't kill the run — they flash yellow and count (debugging by watching).

## Pedagogy-test checklist (what to watch when you trial it)

- [ ] **Time-to-first-win on level 1** — target: under 10 minutes with `--cheat` never needed. If people flounder, shrink `--size` to 5x7.
- [ ] Does anyone *independently* say "can't I write a rule instead of this long plan?" — that's the level-2 handoff working. If nobody does, prompt it: "what's annoying about MOVES?"
- [ ] **Level 2 starter laugh test** — the always-east robot bonking forever should get a laugh, not confusion. It frames failure as information.
- [ ] Do the staged hints in `my_solver.py` carry people to the right-hand rule, or do they need the recipe on a slide? (If slide needed: the 4-step try-order in the file is the slide.)
- [ ] **The level-3 moment** — watch faces when the 5/5 banner lands. If that hits, this earns a slide and a permanent slot.
- [ ] Does 20 minutes hold, or does it want 30? (Level 1: ~8 min · level 2: ~10 · level 3: ~2 + debrief.)
- [ ] AI-era variant worth testing: let students ask their AI for the level-2 function *with the view-dict spec pasted in* — then Run-Gate it. Does that land better or worse than hand-writing?

## Instructor solutions (spoilers)

Level 1, default maze (`--seed 7`, 6x9) — or run `--cheat` for any maze:

```python
MOVES = "ESEENESEENESSESSS"
```

Level 2/3 — the right-hand rule (beats every maze this generator makes, because
recursive-backtracker mazes are "perfect": all walls connected, no loops):

```python
def next_move(view):
    facing = view["facing"]
    for direction in [RIGHT_OF[facing], facing, LEFT_OF[facing],
                      RIGHT_OF[RIGHT_OF[facing]]]:
        if not view["walls"][direction]:
            return direction
```

Anticipated question worth welcoming: "could the robot find the *shortest* path?"
— that's what `--demo` does (breadth-first search, in `play.py`), and it's a
lovely "there's always a deeper level" close.
