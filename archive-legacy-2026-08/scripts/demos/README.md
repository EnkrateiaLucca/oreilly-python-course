# Course automation demos

Runnable example automations, grouped by what they do. Each script is
self-contained: run it with `uv` and the inline dependencies install themselves.

```bash
uv run scripts/demos/<category>/<script>.py [arguments]
```

| Folder | What's inside |
|---|---|
| `file-management/` | Organise a folder by type, classify images with local vision AI, analyse a directory |
| `pdf-documents/` | Summarise a PDF/text file, extract structured fields with a Pydantic schema, chat with a PDF |
| `data-dashboards/` | Build a dashboard from a CSV, fetch an API into SQLite, analyse logs with AI, compare Excel sheets |
| `email-comms/` | Turn Hacker News into an AI briefing, filter messages by urgency, summarise user-research notes |
| `media/` | Transcribe audio to text locally with Whisper |
| `sample-data/` | Inputs you can point the scripts at (CSV, sample PDF, URLs) |

Shared helpers the notebooks import live in `scripts/lib/`; older / redundant
student submissions are kept in `scripts/archive/`.

See [`../../index-scripts.md`](../../index-scripts.md) for a one-line description of every script.

Most AI scripts need an API key (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in `.env`);
`file-management/classify_images.py` and `media/transcribe_audio.py` run fully locally with no key.
