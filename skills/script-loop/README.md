# The SCRIPT loop, as a Claude skill

Drop this folder into any project you want to automate and Claude will run the
course's six-step loop for you — Spot it, Compose the ticket, Request the code,
Inspect before you run, Prove it, Turn it into a tool.

## Install

```bash
mkdir -p ~/my-project/.claude/skills
cp -R skills/script-loop ~/my-project/.claude/skills/
```

Or install it once for every project:

```bash
cp -R skills/script-loop ~/.claude/skills/
```

Then in Claude Code, from that project:

```
/script-loop
```

…or just say what you want to automate ("I want to automate renaming my
downloads") and the skill picks it up.

## What it does

It walks the loop with you and stops at every gate — it will not run generated
code before the Run Gate, and it will not touch real data before a dry run on a
practice copy. That's the point: the loop *is* the guardrail.

You can also enter mid-loop: "is this script safe to run?", "write me a ticket
for this", "wrap this script as a skill".

## Contents

- `SKILL.md` — the procedure Claude follows.
- `references/` — a snapshot of the course [`prompts/`](../../prompts/) folder.
  If you edit the prompts, re-copy them here.
