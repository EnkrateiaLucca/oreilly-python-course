# Demos — Day 2

Day 2 is **three strong automations**, run as three full reps of the **SCRIPT
loop**: **S**pot it, **C**ompose the ticket, **R**equest the code, **I**nspect
before you run, **P**rove it, **T**urn it into a tool. Fewer scripts, more time on
each — you complete the loop, modify the tool, and understand *why* it works.

Each teaches a distinct modern pattern, and the day ends by upgrading one tool you
already understand into an **agent-callable skill** — no new Python, just a
clearer contract.

Every demo ends with a ✏️ Your-turn modification — the tool isn't yours until
you've changed it. Each README follows the same shape: the problem, the ticket,
the prompt that generated the script, how to run it (dry-run first!), how to prove
it worked, and how to turn it into a tool.

| Demo | Pattern it teaches | API key? |
| --- | --- | --- |
| [01-document-inbox](01-document-inbox/) | Messy multimodal documents → **AI + a schema** → one structured action queue | OpenAI |
| [02-data-to-dashboard](02-data-to-dashboard/) | Deterministic Python charts **+** AI judgement: interactive dashboard with an AI read of the patterns | OpenAI (for `--explain`) |
| [03-intelligence-briefing](03-intelligence-briefing/) | APIs + RSS → AI briefing, then **scheduled unattended** (launchd / Task Scheduler) | OpenAI |
| [04-tool-to-skill](04-tool-to-skill/) | **The endpoint:** script → reusable tool → agent-callable skill (+ build-your-own capstone) | Only if your tool needs one |

`reserve/` holds the three retired-from-core automations (downloads organizer,
voice notes, spreadsheet diff) plus extra single-file tools — for fast sessions
and homework. The take-home prompt templates behind every "ticket" and "prompt"
section live in [`../prompts/`](../prompts/).
