# /// script
# requires-python = ">=3.12"
# dependencies = ["rich"]
# ///
"""The Maze — a motivator game for learning to instruct a very literal robot.

You never edit THIS file. Your code lives in my_solver.py (same folder).

  uv run play.py --demo          watch the computer beat the maze (your end goal)
  uv run play.py                 level 1: the robot follows YOUR plan (MOVES string)
  uv run play.py --level 2       level 2: the robot asks your next_move() function
  uv run play.py --level 3       level 3: your next_move() vs 5 random mazes
  uv run play.py --cheat         print a winning MOVES plan for the current maze
  uv run play.py --seed 99       try a different maze layout
"""

import argparse
import importlib.util
import random
import sys
import time
from collections import deque
from pathlib import Path

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

# Directions: compass moves on the grid. N = up a row, E = right a column.
STEP = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}
DEFAULT_SEED = 7


def generate_maze(rows, cols, rng):
    """Carve a perfect maze (every cell reachable, no loops) — recursive backtracker."""
    passages = {(r, c): set() for r in range(rows) for c in range(cols)}
    stack = [(0, 0)]
    visited = {(0, 0)}
    while stack:
        r, c = stack[-1]
        neighbors = []
        for d, (dr, dc) in STEP.items():
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                neighbors.append((d, (nr, nc)))
        if neighbors:
            d, nxt = rng.choice(neighbors)
            passages[(r, c)].add(d)
            passages[nxt].add(OPPOSITE[d])
            visited.add(nxt)
            stack.append(nxt)
        else:
            stack.pop()
    return passages


def shortest_plan(passages, start, goal):
    """BFS: the shortest sequence of moves from start to goal."""
    queue = deque([start])
    came_from = {start: None}
    while queue:
        cell = queue.popleft()
        if cell == goal:
            break
        for d in passages[cell]:
            dr, dc = STEP[d]
            nxt = (cell[0] + dr, cell[1] + dc)
            if nxt not in came_from:
                came_from[nxt] = (cell, d)
                queue.append(nxt)
    moves = []
    cell = goal
    while came_from[cell] is not None:
        cell, d = came_from[cell]
        moves.append(d)
    return "".join(reversed(moves))


def render(passages, rows, cols, player, exit_cell, trail, bump, title, status):
    """Draw the maze as a rich Text grid: walls █, trail ·, player ●, exit ⚑."""
    grid_rows = 2 * rows + 1
    grid_cols = 2 * cols + 1
    lines = [[("█", "grey35") for _ in range(grid_cols)] for _ in range(grid_rows)]
    for (r, c), open_dirs in passages.items():
        gr, gc = 2 * r + 1, 2 * c + 1
        lines[gr][gc] = (" ", "")
        for d in open_dirs:
            dr, dc = STEP[d]
            lines[gr + dr][gc + dc] = (" ", "")
    for r, c in trail:
        lines[2 * r + 1][2 * c + 1] = ("·", "dark_red")
    er, ec = exit_cell
    lines[2 * er + 1][2 * ec + 1] = ("⚑", "bold green")
    pr, pc = player
    lines[2 * pr + 1][2 * pc + 1] = ("●", "bold red" if not bump else "bold yellow")
    text = Text()
    for row in lines:
        for ch, style in row:
            text.append(ch * 2 if ch in "█ ·" else ch + " ", style=style)
        text.append("\n")
    text.append(status, style="italic")
    return Panel(text, title=title, border_style="dark_red", expand=False)


class Game:
    def __init__(self, rows, cols, seed):
        self.rows, self.cols, self.seed = rows, cols, seed
        self.passages = generate_maze(rows, cols, random.Random(seed))
        self.start, self.exit = (0, 0), (rows - 1, cols - 1)
        self.optimal = shortest_plan(self.passages, self.start, self.exit)

    def run(self, get_move, title, animate=True, delay=0.06, max_steps=None):
        """Drive the robot. get_move(view) -> 'N'/'S'/'E'/'W' or None (plan over)."""
        player, facing, steps, bumps = self.start, "E", 0, 0
        trail, memory = [], {}
        max_steps = max_steps or self.rows * self.cols * 6
        outcome = "lost"

        def frame(bump=False, status=""):
            return render(self.passages, self.rows, self.cols, player, self.exit,
                          trail, bump, title, status)

        live = Live(frame(), console=console, refresh_per_second=30) if animate else None
        if live:
            live.start()
        try:
            while steps < max_steps:
                if player == self.exit:
                    outcome = "won"
                    break
                view = {
                    "walls": {d: d not in self.passages[player] for d in "NSEW"},
                    "facing": facing,
                    "position": player,
                    "exit": self.exit,
                    "steps": steps,
                    "memory": memory,
                }
                move = get_move(view)
                if move is None:
                    outcome = "plan ran out"
                    break
                move = str(move).strip().upper()[:1]
                if move not in STEP:
                    raise SystemExit(
                        f"\n😕 Your code returned {move!r} — the robot only knows "
                        f"'N', 'S', 'E', 'W'. Fix my_solver.py and rerun.")
                steps += 1
                if move in self.passages[player]:
                    trail.append(player)
                    dr, dc = STEP[move]
                    player = (player[0] + dr, player[1] + dc)
                    facing = move
                    if live:
                        live.update(frame(status=f"step {steps} · going {move}"))
                else:
                    bumps += 1
                    if live:
                        live.update(frame(bump=True, status=f"step {steps} · BONK — wall to the {move}"))
                if live:
                    time.sleep(delay)
            else:
                outcome = "lost"
            if player == self.exit:
                outcome = "won"
            if live:
                live.update(frame(status=""))
        finally:
            if live:
                live.stop()
        return {"outcome": outcome, "steps": steps, "bumps": bumps,
                "optimal": len(self.optimal), "where": player}


def report(result, level):
    if result["outcome"] == "won":
        msg = (f"🏆 [bold green]MAZE BEATEN[/] in {result['steps']} steps "
               f"(shortest possible: {result['optimal']})")
        if result["bumps"]:
            msg += f" — with {result['bumps']} wall-bonks 😅"
        console.print(Panel(msg, border_style="green"))
    elif result["outcome"] == "plan ran out":
        console.print(Panel(
            f"📜 Your plan ran out at {result['where']} — the flag is at the bottom-right.\n"
            f"Add more moves to MOVES in my_solver.py and rerun. (That loop — edit, run, "
            f"watch — is programming.)", border_style="yellow"))
    else:
        console.print(Panel(
            f"🌀 {result['steps']} steps and the robot is lost (bumps: {result['bumps']}).\n"
            f"Level {level} hint: a maze with all its walls connected can always be beaten "
            f"by keeping one hand on the wall. See the hints in my_solver.py.",
            border_style="yellow"))


def load_solver(path):
    path = Path(path)
    if not path.exists():
        raise SystemExit(f"😕 Can't find your solver file: {path}\n"
                         f"It should sit next to play.py. Did it get renamed?")
    spec = importlib.util.spec_from_file_location("my_solver", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    parser = argparse.ArgumentParser(description="The Maze — instruct a very literal robot.")
    parser.add_argument("--level", type=int, choices=[1, 2, 3], default=1)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED,
                        help=f"maze layout number (default {DEFAULT_SEED}; levels 1-2)")
    parser.add_argument("--size", default="6x9", help="maze size as ROWSxCOLS (default 6x9)")
    parser.add_argument("--solver", default=str(Path(__file__).parent / "my_solver.py"))
    parser.add_argument("--speed", choices=["slow", "normal", "fast"], default="normal")
    parser.add_argument("--no-anim", action="store_true", help="skip animation, print result only")
    parser.add_argument("--demo", action="store_true", help="the computer plays (BFS autopilot)")
    parser.add_argument("--cheat", action="store_true", help="print a winning MOVES plan and exit")
    args = parser.parse_args()

    rows, cols = (int(x) for x in args.size.lower().split("x"))
    delay = {"slow": 0.15, "normal": 0.06, "fast": 0.02}[args.speed]
    animate = not args.no_anim

    if args.cheat:
        game = Game(rows, cols, args.seed)
        console.print(f"A winning plan for maze --seed {args.seed} ({rows}x{cols}):")
        console.print(f'\nMOVES = "{game.optimal}"\n')
        return

    if args.demo:
        game = Game(rows, cols, args.seed)
        plan = iter(game.optimal)
        result = game.run(lambda view: next(plan, None),
                          f"DEMO · autopilot · maze #{args.seed}", animate, delay)
        console.print(Panel("🤖 That was the computer using a path-finding recipe (BFS). "
                            "By level 3, [bold]your[/] code beats any maze too.",
                            border_style="dark_red"))
        report(result, 0)
        return

    solver = load_solver(args.solver)

    if args.level == 1:
        moves = getattr(solver, "MOVES", "")
        plan = iter("".join(moves.split()))  # spaces allowed in the plan
        game = Game(rows, cols, args.seed)
        result = game.run(lambda view: next(plan, None),
                          f"LEVEL 1 · your plan · maze #{args.seed}", animate, delay)
        report(result, 1)
    elif args.level == 2:
        if not hasattr(solver, "next_move"):
            raise SystemExit("😕 Level 2 needs a next_move(view) function in my_solver.py.")
        game = Game(rows, cols, args.seed)
        result = game.run(solver.next_move,
                          f"LEVEL 2 · your logic · maze #{args.seed}", animate, delay)
        report(result, 2)
    else:
        if not hasattr(solver, "next_move"):
            raise SystemExit("😕 Level 3 needs a next_move(view) function in my_solver.py.")
        rng = random.Random()
        trials = [(rng.randrange(1_000_000), 6, 9), (rng.randrange(1_000_000), 8, 12),
                  (rng.randrange(1_000_000), 10, 14), (rng.randrange(1_000_000), 12, 16),
                  (rng.randrange(1_000_000), 14, 20)]
        scores = []
        for i, (seed, r, c) in enumerate(trials, 1):
            game = Game(r, c, seed)
            result = game.run(solver.next_move,
                              f"LEVEL 3 · maze {i}/5 · #{seed} ({r}x{c})", animate, delay)
            scores.append((seed, f"{r}x{c}", result))
        table = Table(title="LEVEL 3 · can your code beat ANY maze?")
        table.add_column("maze"); table.add_column("size")
        table.add_column("result"); table.add_column("steps"); table.add_column("shortest")
        wins = 0
        for seed, size, res in scores:
            won = res["outcome"] == "won"
            wins += won
            table.add_row(f"#{seed}", size,
                          "[green]won[/]" if won else "[red]lost[/]",
                          str(res["steps"]), str(res["optimal"]))
        console.print(table)
        if wins == 5:
            console.print(Panel("🏆 [bold green]YOUR CODE BEATS ANY MAZE.[/] "
                                "You just wrote a general solution — that's the whole "
                                "difference between a plan and a program.",
                                border_style="green"))
        else:
            console.print(Panel(f"{wins}/5 — close. A rule that uses only view['walls'] "
                                "and view['facing'] can win them all. Hints in my_solver.py.",
                                border_style="yellow"))


if __name__ == "__main__":
    main()
