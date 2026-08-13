# Reserve demos

Extra tools for when a session runs fast, someone asks "but could it also...",
or you want more SCRIPT-loop reps at home. Same conventions as the core six.

- `llm.py` — pipe anything into an AI model from your terminal (`cat notes.txt | uv run llm.py "summarize"`); needs `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY` with `-m claude-opus-4-8`).
- `chat_with_pdf.py` — interactive terminal Q&A grounded in one PDF's text; needs `OPENAI_API_KEY`.
- `summarize_document.py` — one-shot bullet-point summary of a .pdf/.txt/.md file; needs `OPENAI_API_KEY`.
- `local_llm.py` — document Q&A + schema-constrained JSON extraction (`ask` / `tasks` / `facts`), fully local via Ollama `gemma4`; no key.
- `track.py` — tiny start/stop/report time-tracker with a JSON-file "database"; no key, stdlib only.
