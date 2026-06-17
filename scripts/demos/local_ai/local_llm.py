#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "ollama>=0.4",
#     "pydantic>=2",
#     "pypdf>=5",
# ]
# ///
"""
Local document Q&A + structured extraction, powered by Ollama.

This does the things the `ollama` CLI cannot: grounded Q&A over a document
and schema-constrained JSON extraction you can pipe into other tools.

Make executable once:   chmod +x ai.py
Run:                    ./ai.py <command> ...   (or: uv run ai.py <command> ...)

Commands:
  ask    PATH                Interactive Q&A grounded in a document
  tasks  PATH                Extract action items as JSON
  facts  PATH                Extract key facts + summary as JSON
  schema PATH SCHEMA.json    Extract using your own JSON schema
                             (or pipe a schema via stdin and pass - as SCHEMA)

All extraction prints JSON to stdout (pipe it: `./ai.py tasks notes.pdf | jq`).
Diagnostics go to stderr so they don't pollute the JSON.

Supports .md, .txt, .pdf (plain-text PDFs).

Set MODEL below to a model you've pulled (`ollama list` shows yours).
"""

import json
import sys
from pathlib import Path

import ollama
from pydantic import BaseModel, Field
from pypdf import PdfReader

# ----- CONFIG -------------------------------------------------------------
MODEL = "gemma4"
# --------------------------------------------------------------------------


# ----- Schemas for the built-in extraction modes --------------------------
class Task(BaseModel):
    description: str = Field(description="What needs to be done")
    owner: str | None = Field(default=None, description="Who is responsible, if stated")
    due: str | None = Field(default=None, description="Deadline if mentioned, else null")
    priority: str | None = Field(
        default=None, description="high, medium, or low if inferable, else null"
    )


class TaskList(BaseModel):
    tasks: list[Task]


class Facts(BaseModel):
    summary: str = Field(description="A 2-3 sentence summary of the document")
    key_facts: list[str] = Field(description="The most important discrete facts")
    entities: list[str] = Field(description="People, orgs, products, or places named")
    dates: list[str] = Field(description="Any dates or time references mentioned")


# ----- IO helpers ---------------------------------------------------------
def log(msg: str) -> None:
    """Diagnostics to stderr, keeping stdout clean for piped JSON."""
    print(msg, file=sys.stderr)


def read_doc(file_path: str) -> str:
    path = Path(file_path).expanduser()
    if not path.exists():
        log(f"File not found: {path}")
        sys.exit(1)
    suffix = path.suffix.lower()
    if suffix in (".md", ".txt"):
        text = path.read_text(encoding="utf-8", errors="replace")
    elif suffix == ".pdf":
        reader = PdfReader(str(path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        log(f"Unsupported file type: {suffix} (use .md, .txt, or .pdf)")
        sys.exit(1)
    if not text.strip():
        log("No text extracted. If it's a scanned PDF, it needs OCR.")
        sys.exit(1)
    log(f"Loaded '{path.name}' ({len(text)} characters).")
    return text


# ----- Core: schema-constrained extraction --------------------------------
def extract(document: str, schema: dict, instruction: str) -> dict:
    """Constrain the model to a JSON schema and return parsed JSON.

    Uses Ollama's `format` parameter (constrained decoding) plus
    temperature 0 for deterministic, schema-valid output.
    """
    response = ollama.chat(
        model=MODEL,
        format=schema,
        options={"temperature": 0},
        messages=[
            {
                "role": "system",
                "content": (
                    f"{instruction} Use only the document below. "
                    "Respond as JSON only, no commentary. If a field cannot be "
                    "filled from the document, use null rather than inventing a value."
                ),
            },
            {"role": "user", "content": document},
        ],
    )
    return json.loads(response["message"]["content"])


def emit(data: dict) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


# ----- Commands ------------------------------------------------------------
def cmd_tasks(file_path: str) -> None:
    doc = read_doc(file_path)
    result = extract(
        doc,
        TaskList.model_json_schema(),
        "Extract every actionable task or action item from the document.",
    )
    emit(result)


def cmd_facts(file_path: str) -> None:
    doc = read_doc(file_path)
    result = extract(
        doc,
        Facts.model_json_schema(),
        "Extract a summary, key facts, named entities, and dates from the document.",
    )
    emit(result)


def cmd_schema(file_path: str, schema_arg: str) -> None:
    if schema_arg == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(schema_arg).expanduser().read_text(encoding="utf-8")
    try:
        schema = json.loads(raw)
    except json.JSONDecodeError as e:
        log(f"Invalid JSON schema: {e}")
        sys.exit(1)
    doc = read_doc(file_path)
    result = extract(
        doc,
        schema,
        "Extract data from the document into the provided JSON schema.",
    )
    emit(result)


def cmd_ask(file_path: str) -> None:
    doc = read_doc(file_path)
    log("Ask questions about the document. Type 'exit' or 'quit' to stop.\n")
    history = [
        {
            "role": "system",
            "content": (
                "Answer using only the document below. If the answer is not in "
                f"it, say so.\n\n--- DOCUMENT ---\n{doc}\n--- END DOCUMENT ---"
            ),
        }
    ]
    while True:
        try:
            q = input("you > ").strip()
        except (EOFError, KeyboardInterrupt):
            print(file=sys.stderr)
            break
        if q.lower() in ("exit", "quit"):
            break
        if not q:
            continue
        history.append({"role": "user", "content": q})
        reply = ollama.chat(model=MODEL, messages=history)["message"]["content"]
        history.append({"role": "assistant", "content": reply})
        print(f"\nai  > {reply}\n", file=sys.stderr)


# ----- Dispatch ------------------------------------------------------------
def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    cmd, rest = args[0], args[1:]

    if cmd == "ask" and len(rest) == 1:
        cmd_ask(rest[0])
    elif cmd == "tasks" and len(rest) == 1:
        cmd_tasks(rest[0])
    elif cmd == "facts" and len(rest) == 1:
        cmd_facts(rest[0])
    elif cmd == "schema" and len(rest) == 2:
        cmd_schema(rest[0], rest[1])
    else:
        print(__doc__)


if __name__ == "__main__":
    main()