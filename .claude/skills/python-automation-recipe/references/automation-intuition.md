# Automation Intuition (course distillation)

Source: `oreilly-python-course/notebooks/03-automation-projects/00-automation-intuition.md`.
Read this before Step 1–2 of the skill workflow.

## The core mental model: Input → Process → Output

```
INPUT  ──►  PROCESS  ──►  OUTPUT
```

| Question     | Examples                                                              |
|--------------|-----------------------------------------------------------------------|
| **Input?**   | A folder, a CSV, a URL, a PDF, clipboard, an API response             |
| **Process?** | Rename, filter, extract, summarize, convert, merge, call an LLM       |
| **Output?**  | A new file, a printed report, an email, a row added to a sheet        |

If the student can fill these three blanks in one sentence, they have a script. If they can't, the skill's job is to push them until they can.

## The sniff test — is it worth automating?

1. Do I do this more than once? (Twice is a coincidence. Three times is a script.)
2. Are the steps predictable? (Describe it to a friend in under a minute.)
3. Does the input live somewhere a computer can reach?
4. Is the output something a computer can produce?

4 yeses → strong candidate. 2 or fewer → don't automate yet.

## The 5 categories (use these as `AskUserQuestion` option labels)

- **Files & folders** — filesystem ops (rename, sort, backup, dedupe).
- **Text & structured data** — CSV/JSON/PDF transforms, extraction, cleaning.
- **The web** — URLs, public APIs, static scraping.
- **App integrations** — glue between two tools (Gmail→Slack, Calendar→Notion).
- **AI-powered** — judgment / language tasks (summarize, classify, extract).

## Vague idea → runnable script, in 4 steps

1. **One-sentence spec**: "Take \<input\>, do \<process\>, produce \<output\>."
2. **Draft with AI** using a tight prompt template.
3. **Run it**: `uv run python scripts/my_tool.py --input ./folder --output emails.csv`
4. **Wrap it in a CLI**: argparse + `--help`, save to `scripts/`. That's a real tool.

## Red flags (probably wrong hammer)

- Rules change every time → needs human judgment.
- Input isn't reachable (only in the student's head, or behind 2FA without an API).
- Faster to do once by hand and never again.
- Bug consequences are expensive or irreversible.
