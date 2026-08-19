---
marp: true
theme: automata
paginate: true
---

<!-- _class: lead dark -->
<!-- _paginate: false -->

<div class="kicker">Automata Learning Lab · O'Reilly Live Training</div>

# Automate Tasks with <em>Python + AI</em>

The whole course on one wall — the essentials, the loop, the takeaways.

---

<div class="kicker">Recap</div>

## What we'll cover

1) **The Python you actually need** — reading vocabulary, not writing skill
2) **The SCRIPT loop** — the six-step formula behind every automation
3) **The patterns & the takeaways** — what to do Monday morning

---

<!-- _class: dark quote -->

> <span class="mark">"</span>You don't need to learn to write Python. You need to learn to <em>read</em> it, <em>run</em> it, and <em>steer</em> the AI that writes it.<span class="mark">"</span>

<div class="by">— The premise of the whole course</div>

---

<div class="kicker">Day 1</div>

## The reading vocabulary

<div class="bento">
<div class="cell wide"><h3>print · variables · f-strings</h3><p>How a script narrates what it's doing. Follow the prints, follow the story.</p></div>
<div class="cell"><h3>lists · for loops</h3><p>Hold many things, do one thing to each.</p></div>
<div class="cell"><h3>if / elif / else · def</h3><p>The decision at the heart of every tool.</p></div>
<div class="cell"><h3>pathlib.Path</h3><p>Real files and folders — where blast radius lives.</p></div>
<div class="cell wide"><h3>imports · the PEP 723 header · tracebacks</h3><p>What the script borrows, and how it tells you it broke.</p></div>
</div>

---

<!-- _class: dark -->

<div class="kicker">Anatomy of an AI-generated script</div>

```python
# /// script                     ← PEP 723: uv reads this, installs, runs
# requires-python = ">=3.12"
# dependencies = ["requests"]    ← CHECK THESE ON pypi.org
# ///
from pathlib import Path         ← what it can touch

def folder_for(name: str) -> str:   ← the decision
    return "Documents" if name.endswith(".pdf") else "Other"

if args.apply:                   ← nothing happens without this flag
    file.rename(target)
```

*One file. No environment to manage. `uv run script.py`.*

---

## Reading the wreckage

<div class="two-col">
<div>

### A traceback in 10 seconds
* Read the **last line first** — the error type and message
* Then the **file + line number** just above it
* Everything in between is the path that got you there

</div>
<div>

### Then
* `try / except` = the script expected this failure
* Paste the last line into the AI — it's the best bug report you can give
* A crash is a **message**, not a disaster

</div>
</div>

---

## APIs, and then AI APIs — the same dance

<div class="flow">
<div class="step"><h3>Build</h3><p>A precisely worded request</p></div>
<div class="arrow">→</div>
<div class="step"><h3>Send</h3><p>requests.get() / client.create()</p></div>
<div class="arrow">→</div>
<div class="step"><h3>Read</h3><p>Structured data back</p></div>
</div>

* Weather API, Hacker News, OpenAI, Anthropic, local Ollama — **one pattern**
* The only difference: AI counters **check ID** — an API key, from `.env`, never pasted in code
* Local models (Ollama): no key, no internet, free — and your data never leaves the machine

---

<!-- _class: dark lead -->

<div class="kicker">The formula</div>

# The <em>SCRIPT</em> loop

Every automation in this course was built the same six ways.

---

## S · C · R · I · P · T

<div class="flow">
<div class="step"><h3>S — Spot</h3><p>Is it worth automating?</p></div>
<div class="arrow">→</div>
<div class="step"><h3>C — Compose</h3><p>The ticket</p></div>
<div class="arrow">→</div>
<div class="step"><h3>R — Request</h3><p>The code</p></div>
</div>

<div class="flow">
<div class="step"><h3>I — Inspect</h3><p>The Run Gate</p></div>
<div class="arrow">→</div>
<div class="step"><h3>P — Prove</h3><p>Dry run → apply</p></div>
<div class="arrow">→</div>
<div class="step"><h3>T — Turn</h3><p>Into a tool</p></div>
</div>

*Read it. Bound it. Run it. Prove it.*

---

<!-- _class: dark -->

<div class="kicker">C — Compose the ticket</div>

```text
TASK:        one sentence — what should happen
TRIGGER:     manual / every morning at 8 / when a file lands
TOUCHES:     the exact folders, files, sites, accounts
MUST NEVER:  never delete, never send, never leave folder X
DONE MEANS:  the concrete result you will check by hand
```

*A vague ask produces a vague — and riskier — script. Write the spec first.*

---

## I — The Run Gate

**AI-generated code is untrusted input.** Five questions, two minutes:

| Does it… | Look for | If yes |
|---|---|---|
| Write / move / delete files? | `shutil`, `os.remove`, `open(...,"w")` | Demand dry-run + `--apply` |
| Touch the network? | `requests`, any SDK | Know *which* sites, and what leaves |
| Read secrets? | `os.environ`, `.env` | Keys from `.env`, never in code |
| Run other code? 🚩 | `subprocess`, `eval`, `exec` | **Stop.** Ask why |
| Run unattended? | your own TRIGGER | Everything above gets stricter |

---

## The package check

<div class="stat-grid">
<div class="stat"><div class="num">1 in 5</div><div class="label">AI-suggested packages that don't exist</div></div>
<div class="stat"><div class="num">30s</div><div class="label">To verify a name on pypi.org</div></div>
<div class="stat"><div class="num">0</div><div class="label">Typos that are "close enough"</div></div>
</div>

*Attackers register hallucinated package names and ship malware — "slopsquatting".
Read the `dependencies = [...]` line. Every time.*

---

## P — Prove it

1) `uv run tool.py --help` — does it describe what you asked for?
2) **Dry run.** Read every line of what it *would* do.
3) `--apply` on a **practice copy** — never the real folder first.
4) Check your ticket's **DONE MEANS** by hand. Red → Green.

> You can debug a wrong output. You can't un-delete a folder.

---

## T — The continuum

<div class="timeline">
<div class="pt"><div class="dot"></div><div class="when">One-off</div><div class="what">A script that ran once</div></div>
<div class="pt"><div class="dot"></div><div class="when">Reusable tool</div><div class="what">Alias it — `alias briefing=...`</div></div>
<div class="pt"><div class="dot"></div><div class="when">Scheduled</div><div class="what">launchd / Task Scheduler</div></div>
<div class="pt"><div class="dot"></div><div class="when">Agent skill</div><div class="what">One markdown contract</div></div>
</div>

**The script is cheap. The reusable capability is the asset.**

---

<div class="kicker">Day 2</div>

## Three automations, three patterns

<div class="bento">
<div class="cell wide"><h3>Document inbox</h3><p>Messy multimodal pile → <em>AI + a schema</em> → one structured action queue you can sort and act on.</p></div>
<div class="cell"><h3>Data → dashboard</h3><p>Deterministic Python charts <em>plus</em> AI judgement on what the patterns mean.</p></div>
<div class="cell"><h3>Intelligence briefing</h3><p>APIs + RSS → AI summary, running <em>unattended</em> on a schedule.</p></div>
<div class="cell wide"><h3>Tool → skill</h3><p>Clear inputs, clear outputs, safe defaults, a usage contract. Nothing about the Python changes — you just write the contract where an agent can read it.</p></div>
</div>

---

## Before you build: does this already exist?

<div class="two-col">
<div>

### Ask first
* Is there a **built-in OS feature** or free app?
* Is there a **no-code service** (Shortcuts, Zapier, n8n)?
* Verdict: **BUY / USE BUILT-IN / BUILD**

</div>
<div>

### Good reasons to BUILD
* It touches **local files** no web service can reach
* It needs **your logic** or your prompt in the middle
* It should run **on your machine** — privacy, no subscription
* The alternatives cost more than 30 minutes

</div>
</div>

---

## Takeaways

* **Reading beats writing.** You can follow any script's story: input → process → output.
* **The ticket is the skill.** If you can't write DONE MEANS, you can't verify it — and you shouldn't schedule it.
* **Treat AI code like mail from a stranger.** Blast radius, package check, follow the story.
* **Dry run by default.** Every tool you keep should refuse to act without `--apply`.
* **Hoard your tools.** Script + ticket + prompt, saved together. That's the compounding asset.

---

<!-- _class: dark lead -->
<!-- _paginate: false -->

<div class="kicker">One page to take home</div>

# Read it. Bound it. <em>Run it.</em> Prove it.

`prompts/script-loop.md` — the whole course on one card.
