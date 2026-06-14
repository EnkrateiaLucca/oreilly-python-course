# Demos: automation cookbook

These are the automations shown live in the course, grouped into the four
categories the slides walk through. Most grew out of real questions students
asked during the trainings. Each folder holds three demos.

Run any of them with `uv` (inline dependencies, nothing to install first):

```bash
uv run scripts/demos/<folder>/<script>.py [arguments]
```

## file-management

| Script | What it teaches | Needs |
|---|---|---|
| `1_file_organizer.py` | **Organise a messy folder** by file type into documents/media/others. Dry-run by default; pass `--apply` to actually move. | folder arg |
| `3_file_image_classifier.py` | **Local vision AI** — classify images into folders using a local Ollama model. No API key. | Ollama + `qwen2.5vl` running locally |
| `4_file_dir_analysis.py` | **Analyse a directory** by file type/size and generate tables + a visual summary chart. | folder arg |

## pdf-documents

| Script | What it teaches | Needs |
|---|---|---|
| `1_pdf_summarizer.py` | **Summarise any PDF** from a URL in one command. | OpenAI key, PDF URL arg |
| `2_pdf_receipt_extractor.py` | **Structured extraction** — pull typed fields (company, date, amount) out of text with a Pydantic schema. | OpenAI key, text file arg |
| `5_pdf_chat.py` | **Interactive AI tool** — a terminal chat that extracts a CSV from a PDF on request. | OpenAI key, PDF arg |

## data-dashboards

| Script | What it teaches | Needs |
|---|---|---|
| `2_JG_api_data_storage.py` | **Fetch live API data** and persist it in a local SQLite database. | internet (public APIs, no key) |
| `3_csv_dashboard.py` | **Data visualization** — auto-build a web dashboard (time series / distribution / category) from any CSV. | CSV path arg |
| `5_VK_log_analyzer.py` | **Analyse log files with AI** — spot patterns and generate charts. | Anthropic key |

## email-comms

| Script | What it teaches | Needs |
|---|---|---|
| `1_AH_news_summarizer.py` | **Summarise daily news feeds** from RSS into an AI briefing. | Anthropic key, internet |
| `2_SW_email_urgency_filter.py` | **AI text classification** — sort messages by urgency and topic (runs on simulated data). | Anthropic key |
| `4_VN_user_test_summarizer.py` | **Summarise user-research notes** into structured insights with AI. | Anthropic key |

`sample-data/` holds inputs you can point these at (a CSV, a sample PDF, URLs,
saved news data). Shared helpers the notebooks import live in `scripts/lib/`.

> Additional student submissions that were redundant with these or niche live in
> `scripts/archive/demos/` rather than being deleted, so the ideas are still there
> for reference.
