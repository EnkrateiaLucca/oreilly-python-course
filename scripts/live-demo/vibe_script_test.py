#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "openai>=1.60.0",
# ]
# ///

"""
doc_analyzer.py

Usage:
  OPENAI_API_KEY=... ./doc_analyzer.py file1.txt [file2.txt ...]
  OPENAI_API_KEY=... uv run doc_analyzer.py file1.txt

- Reads one or more .txt files (or directories containing .txt files)
- Sends each file’s contents to the OpenAI Responses API
- Returns:
    * summary
    * key_facts (extracted data)
    * bullet_explanations (teaching-style bullets)
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

from openai import OpenAI


ANALYSIS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
            "description": "A concise summary of the document (3–5 sentences).",
        },
        "key_facts": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Short bullet points capturing key factual data, figures, entities, or events.",
        },
        "bullet_explanations": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Teaching-style bullet points that explain core ideas in clear, simple language.",
        },
    },
    "required": ["summary", "key_facts", "bullet_explanations"],
    "additionalProperties": False,
}


def iter_input_files(paths: Iterable[str]) -> Iterable[Path]:
    """Yield all text files from the given paths.

    - If a path is a file: yield it (regardless of extension).
    - If a path is a directory: yield all *.txt files under it (non-recursive).
    """
    for raw in paths:
        p = Path(raw).expanduser()
        if p.is_file():
            yield p
        elif p.is_dir():
            for child in sorted(p.glob("*.txt")):
                if child.is_file():
                    yield child
        else:
            print(f"[WARN] Path not found: {p}", file=sys.stderr)


def read_text_file(path: Path, encoding: str = "utf-8") -> str:
    return path.read_text(encoding=encoding)


def create_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    # The OpenAI client reads OPENAI_API_KEY from the environment by default,
    # but we pass it explicitly for clarity.
    return OpenAI(api_key=api_key)


def analyze_text(
    client: OpenAI,
    text: str,
    model: str = "gpt-4.1-mini",
    max_output_tokens: int = 800,
) -> Dict[str, Any]:
    """Call the Responses API to analyze a document and return a structured dict."""
    instructions = (
        "You are a precise document analyst.\n"
        "Given the input document text, you must produce JSON that matches "
        "the provided JSON schema. Do not include any commentary outside JSON.\n\n"
        "The JSON must include:\n"
        "  - 'summary': a concise 3–5 sentence summary.\n"
        "  - 'key_facts': bullet-style strings capturing important data, entities, and numbers.\n"
        "  - 'bullet_explanations': bullet-style strings explaining core ideas for a smart beginner.\n"
    )

    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=text,
        text={
            "format": {
                "type": "json_schema",
                "name": "document_analysis",
                "schema": ANALYSIS_SCHEMA,
                "strict": True,
            }
        },
        max_output_tokens=max_output_tokens,
    )

    # Prefer response.output_text, but fall back to reconstructing from response.output
    raw_json: str | None = None

    # Newer library versions usually provide `output_text`
    if hasattr(response, "output_text"):
        raw_json = getattr(response, "output_text", None)  # type: ignore[attr-defined]

    # Fallback: manually collect text chunks from `response.output`
    if not raw_json:
        chunks: List[str] = []
        output = getattr(response, "output", []) or []
        for item in output:
            content_list = getattr(item, "content", []) or []
            for content in content_list:
                ctype = getattr(content, "type", None)
                if ctype in ("output_text", "output_text_delta", "text"):
                    # different client versions may use different attribute names
                    if hasattr(content, "text"):
                        chunks.append(str(content.text))
                    elif hasattr(content, "value"):
                        chunks.append(str(content.value))
        if chunks:
            raw_json = "".join(chunks)

    if not raw_json:
        raise RuntimeError("Could not extract text payload from Responses API response.")

    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Model returned invalid JSON. Raw payload was:\n{raw_json}"
        ) from e

    return data


def format_result(filename: Path, result: Dict[str, Any]) -> str:
    """Format a single file's analysis as Markdown-ish text for the terminal."""
    summary = result.get("summary", "").strip()
    key_facts = result.get("key_facts") or []
    bullet_explanations = result.get("bullet_explanations") or []

    lines: List[str] = []
    lines.append("=" * 80)
    lines.append(f"File: {filename}")
    lines.append("=" * 80)
    lines.append("")
    lines.append("# Summary")
    lines.append(summary if summary else "(no summary returned)")
    lines.append("")
    lines.append("# Key facts")
    if key_facts:
        for fact in key_facts:
            lines.append(f"- {fact}")
    else:
        lines.append("- (no key facts returned)")
    lines.append("")
    lines.append("# Bullet point explanations")
    if bullet_explanations:
        for bullet in bullet_explanations:
            lines.append(f"- {bullet}")
    else:
        lines.append("- (no bullet explanations returned)")
    lines.append("")

    return "\n".join(lines)


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize and extract data from text files using the OpenAI Responses API."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Paths to text files or directories containing .txt files.",
    )
    parser.add_argument(
        "--model",
        default="gpt-4.1-mini",
        help="Model name to use (default: gpt-4.1-mini).",
    )
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=800,
        help="Maximum number of output tokens (default: 800).",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> None:
    args = parse_args(argv or sys.argv[1:])

    files = list(iter_input_files(args.paths))
    if not files:
        print("No valid files found.", file=sys.stderr)
        sys.exit(1)

    client = create_client()

    for path in files:
        try:
            text = read_text_file(path)
        except Exception as e:  # noqa: BLE001
            print(f"[ERROR] Failed to read {path}: {e}", file=sys.stderr)
            continue

        if not text.strip():
            print(f"[WARN] File is empty or whitespace only: {path}", file=sys.stderr)
            continue

        try:
            result = analyze_text(
                client,
                text=text,
                model=args.model,
                max_output_tokens=args.max_output_tokens,
            )
        except Exception as e:  # noqa: BLE001
            print(f"[ERROR] Analysis failed for {path}: {e}", file=sys.stderr)
            continue

        print(format_result(path, result))


if __name__ == "__main__":
    main()