# Demos — Day 2

Every folder here is one rep of the **SCRIPT loop**: **S**pot it, **C**ompose
the ticket, **R**equest the code, **I**nspect before you run, **P**rove it,
**T**urn it into a tool.

Every demo ends with a ✏️ Your-turn modification — the tool isn't yours until
you've changed it.

Each demo README follows the same shape — the problem, the ticket, the prompt
that generated the script, how to run it (dry-run first!), how to prove it
worked, and how to ship it as an everyday tool.

| Demo | What it does | API key? | Ollama? |
| --- | --- | --- | --- |
| [01-tame-your-downloads](01-tame-your-downloads/) | Sort a messy folder by type; bonus: sort images by content with local AI | No | Bonus only |
| [02-invoices-to-spreadsheet](02-invoices-to-spreadsheet/) | Folder of invoices -> typed fields -> one CSV | OpenAI | No |
| [03-csv-to-dashboard](03-csv-to-dashboard/) | Any CSV -> interactive browser dashboard | No | No |
| [04-voice-notes-to-text](04-voice-notes-to-text/) | Voice note -> local transcript -> AI summary + action items | Anthropic* | No |
| [05-morning-briefing](05-morning-briefing/) | Hacker News -> AI briefing, then SCHEDULE it (launchd / Task Scheduler) | OpenAI | No |
| [06-spreadsheet-diff](06-spreadsheet-diff/) | Two Excel files -> every changed cell, highlighted | No | No |
| [07-your-first-tool](07-your-first-tool/) | **Capstone:** you build your own tool with the full SCRIPT loop | Only if your tool needs one | No |

\* demo 04 runs fully local (no key) with `--no-summary`.

`reserve/` holds five extra tools for fast sessions and homework.
The take-home prompt templates behind every "ticket" and "prompt" section live
in [`../prompts/`](../prompts/).
