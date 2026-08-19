# Prompt

The take-home for the **T** step, upgraded. A script you can run is not yet a tool
someone else — a teammate, future-you, or an AI agent — can use reliably. Two
short passes turn a script into a *capability*.

> The script is cheap. The reusable capability is the asset.
> Continuum: **one-off automation → reusable tool → scheduled tool → agent-callable skill.**

## Pass 1 — Is it a reusable tool? (four requirements)

Before you call any automation "done", make sure you can answer all four. Nothing
here needs new code — mostly it's `--help`, safe defaults, and one written note.

- [ ] **Clear inputs** — exactly what it takes: arguments, files, environment vars.
      (`uv run tool.py --help` should say so.)
- [ ] **Clear outputs** — exactly what it returns or changes, and where.
- [ ] **Safe defaults** — dry-run by default, bounded scope, friendly failures
      (a plain-English fix message, never a raw traceback).
- [ ] **Usage contract** — a short note: when to use it, how to call it, what it
      must never do. (This is your automation ticket, kept next to the tool.)

## Pass 2 — Make it agent-callable (optional)

If a tool already passes Pass 1, it is already agent-ready — you just write its
usage contract in a form an agent reads. That form is a **skill**: one markdown
file. **Nothing about the Python changes.**

### The skill wrapper template

```markdown
---
name: <short-tool-name>
description: <one sentence: what capability this gives an agent>
---

# Skill: <tool name>

## When to use
<The trigger. When SHOULD an agent reach for this — and when should it not?>

## Inputs
<Arguments, files, and environment variables it needs.>

## Command to run
​```bash
uv run path/to/tool.py <args>          # preview (writes nothing)
uv run path/to/tool.py <args> --apply  # act
​```

## Expected output
<What a successful run prints and/or writes.>

## Safety constraints
<The MUST NEVER lines from your ticket. An agent has a bigger reach than you —
so these matter MORE, not less.>
```

A worked example wrapping the document-inbox tool lives in
[`../demos/04-tool-to-skill/SKILL.md`](../demos/04-tool-to-skill/SKILL.md).

## Why this is the right endpoint

- The same **Run Gate** thinking applies — an agent just has a bigger blast
  radius, so bounded scope and safe defaults carry more weight.
- You don't have to build agents to benefit: writing the six fields forces you to
  state the tool's contract clearly, which makes it better for humans too.
- Most tools stop at "reusable" or "scheduled" — and that's fine. The point is to
  *see the whole ladder* and know which rung a given chore needs.

## How to read the verdict

_(Placeholder — the verdict is Pass 1's four checkboxes. All four ticked → it's a
reusable tool. Pass 2 is optional: only wrap it as a skill if an agent will call it.)_
