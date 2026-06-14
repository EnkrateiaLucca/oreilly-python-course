# Index of Course Examples

Each script is self-contained and runnable with `uv` (inline dependencies):

```bash
uv run scripts/demos/<category>/<script>.py [arguments]
```

Shared helpers the notebooks import live in `scripts/lib/`. Sample inputs live in
`scripts/demos/sample-data/`. Older / redundant student submissions are kept in
`scripts/archive/`.

---

## File Management (`scripts/demos/file-management`)

- [`organize_folder.py`](scripts/demos/file-management/organize_folder.py) — Sort a messy folder into subfolders by file type (dry-run by default, `--apply` to move)
- [`classify_images.py`](scripts/demos/file-management/classify_images.py) — Categorise images into folders using a local Ollama vision model (no API key)
- [`analyze_directory.py`](scripts/demos/file-management/analyze_directory.py) — Analyse a directory by type/size and generate tables plus a summary chart

## PDF / Documents (`scripts/demos/pdf-documents`)

- [`summarize_document.py`](scripts/demos/pdf-documents/summarize_document.py) — Summarise any PDF or text file in one command
- [`extract_receipt_fields.py`](scripts/demos/pdf-documents/extract_receipt_fields.py) — Pull typed fields (company, date, amount) out of text with a Pydantic schema
- [`chat_with_pdf.py`](scripts/demos/pdf-documents/chat_with_pdf.py) — Interactive terminal chat that extracts a CSV from a PDF on request

## Data / Dashboards (`scripts/demos/data-dashboards`)

- [`csv_dashboard.py`](scripts/demos/data-dashboards/csv_dashboard.py) — Build an interactive web dashboard from any CSV
- [`api_to_database_JG.py`](scripts/demos/data-dashboards/api_to_database_JG.py) — Fetch data from public APIs and persist it in a local SQLite database
- [`analyze_logs_VK.py`](scripts/demos/data-dashboards/analyze_logs_VK.py) — Analyse log files with AI and produce matplotlib charts
- [`compare_excel_sheets.py`](scripts/demos/data-dashboards/compare_excel_sheets.py) — Compare two Excel sheets and highlight every changed cell

## Email / Comms (`scripts/demos/email-comms`)

- [`news_briefing.py`](scripts/demos/email-comms/news_briefing.py) — Fetch top Hacker News stories and turn them into an AI briefing
- [`email_urgency_filter_SW.py`](scripts/demos/email-comms/email_urgency_filter_SW.py) — Classify messages by urgency and topic with AI (runs on simulated data)
- [`summarize_user_research_VN.py`](scripts/demos/email-comms/summarize_user_research_VN.py) — Summarise user-research / test notes into structured insights with AI

## Media (`scripts/demos/media`)

- [`transcribe_audio.py`](scripts/demos/media/transcribe_audio.py) — Transcribe an audio file to text locally with faster-whisper (no API key)
