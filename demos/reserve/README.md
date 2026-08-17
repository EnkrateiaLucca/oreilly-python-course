# Reserve demos

Extra tools for when a session runs fast, someone asks "but could it also...",
or you want more SCRIPT-loop reps at home. Same conventions as the three core
automations.

## Retired-from-core automations (still great reps)

Day 2 now runs three strong automations; these three used to be in the core set
and make excellent homework — each is a full SCRIPT-loop rep with its own README.

- `downloads-organizer/` — sort a messy folder by file type; bonus `classify_images.py` sorts images by *content* with a local Ollama vision model. No key (bonus needs Ollama).
- `voice-notes/` — a voice memo → local Whisper transcript → AI summary + action items. Needs `ANTHROPIC_API_KEY` (or `--no-summary` for fully local).
- `spreadsheet-diff/` — compare two Excel files and highlight every changed cell. No key, no AI — a reminder that plain Python is often enough.

## Extra single-file tools

- `llm.py` — pipe anything into an AI model from your terminal (`cat notes.txt | uv run llm.py "summarize"`); needs `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY` with `-m claude-opus-4-8`).
- `chat_with_pdf.py` — interactive terminal Q&A grounded in one PDF's text; needs `OPENAI_API_KEY`.
- `summarize_document.py` — one-shot bullet-point summary of a .pdf/.txt/.md file; needs `OPENAI_API_KEY`.
- `local_llm.py` — document Q&A + schema-constrained JSON extraction (`ask` / `tasks` / `facts`), fully local via Ollama `gemma4`; no key.
- `track.py` — tiny start/stop/report time-tracker with a JSON-file "database"; no key, stdlib only.
