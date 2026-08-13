# /// script
# requires-python = ">=3.12"
# dependencies = ["ollama", "pydantic", "pypdf"]
# ///
"""Local document Q&A + structured JSON extraction, powered by Ollama.

Everything runs on your machine — no API key, nothing leaves your laptop.
Extraction prints clean JSON to stdout (diagnostics go to stderr), so you can
pipe it:  uv run demos/reserve/local_llm.py tasks notes.pdf | jq

Run it like:
    uv run demos/reserve/local_llm.py ask   notes.pdf     # interactive Q&A
    uv run demos/reserve/local_llm.py tasks notes.pdf     # action items as JSON
    uv run demos/reserve/local_llm.py facts notes.pdf     # summary + facts as JSON

Needs: Ollama running locally with the model pulled once:  ollama pull gemma4
Supports .md, .txt and text-based .pdf files.
"""

import argparse
import json
import sys
from pathlib import Path

import ollama
from pydantic import BaseModel, Field
from pypdf import PdfReader

MODEL = "gemma4"


# The schemas ARE the spec: Ollama's `format` parameter constrains the model's
# output to this exact JSON shape (constrained decoding — not just hoping).
class Task(BaseModel):
    description: str = Field(description="What needs to be done")
    owner: str | None = Field(default=None, description="Who is responsible, if stated")
    due: str | None = Field(default=None, description="Deadline if mentioned, else null")


class TaskList(BaseModel):
    tasks: list[Task]


class Facts(BaseModel):
    summary: str = Field(description="A 2-3 sentence summary of the document")
    key_facts: list[str] = Field(description="The most important discrete facts")
    entities: list[str] = Field(description="People, orgs, products, or places named")


def log(msg: str) -> None:
    """Diagnostics go to stderr so stdout stays clean for piped JSON."""
    print(msg, file=sys.stderr)


def require_ollama() -> None:
    """Fail with a friendly fix message if Ollama isn't reachable."""
    try:
        ollama.list()
    except Exception:
        log("Could not reach Ollama on this machine.")
        log("1) Install it from https://ollama.com and start the app")
        log(f"2) Pull the model once with:  ollama pull {MODEL}")
        sys.exit(1)


def read_doc(file_path: str) -> str:
    path = Path(file_path).expanduser()
    if not path.exists():
        log(f"File not found: {path}")
        sys.exit(1)
    if path.suffix.lower() in (".md", ".txt"):
        text = path.read_text(encoding="utf-8", errors="replace")
    elif path.suffix.lower() == ".pdf":
        text = "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
    else:
        log(f"Unsupported file type: {path.suffix} (use .md, .txt, or .pdf)")
        sys.exit(1)
    if not text.strip():
        log("No text extracted. A scanned PDF needs OCR first.")
        sys.exit(1)
    log(f"Loaded '{path.name}' ({len(text)} characters).")
    return text


def extract(document: str, schema: dict, instruction: str) -> dict:
    response = ollama.chat(
        model=MODEL,
        format=schema,                      # constrain output to the JSON schema
        options={"temperature": 0},         # deterministic extraction
        messages=[
            {"role": "system",
             "content": (f"{instruction} Use only the document below. If a field "
                         "cannot be filled from it, use null — never invent values.")},
            {"role": "user", "content": document},
        ],
    )
    return json.loads(response["message"]["content"])


def cmd_ask(document: str) -> None:
    log("Ask questions about the document. Type 'exit' to stop.\n")
    history = [{"role": "system",
                "content": ("Answer using only the document below. If the answer "
                            f"is not in it, say so.\n\n{document}")}]
    while True:
        try:
            question = input("you > ").strip()
        except (EOFError, KeyboardInterrupt):
            log("")
            break
        if question.lower() in ("exit", "quit"):
            break
        if not question:
            continue
        history.append({"role": "user", "content": question})
        reply = ollama.chat(model=MODEL, messages=history)["message"]["content"]
        history.append({"role": "assistant", "content": reply})
        log(f"\nai  > {reply}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Local document Q&A and JSON extraction with Ollama.")
    parser.add_argument("command", choices=["ask", "tasks", "facts"],
                        help="ask = interactive Q&A, tasks/facts = JSON extraction")
    parser.add_argument("file", help="Path to a .md, .txt or .pdf document")
    args = parser.parse_args()

    require_ollama()
    document = read_doc(args.file)

    if args.command == "ask":
        cmd_ask(document)
    elif args.command == "tasks":
        result = extract(document, TaskList.model_json_schema(),
                         "Extract every actionable task or action item from the document.")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.command == "facts":
        result = extract(document, Facts.model_json_schema(),
                         "Extract a summary, key facts, and named entities from the document.")
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
