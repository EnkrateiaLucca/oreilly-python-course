# /// script
# requires-python = ">=3.12"
# dependencies = ["openai", "anthropic", "python-dotenv"]
# ///
"""A tiny `llm`-style command: send text to an AI model from your terminal.

Reads from stdin, so it becomes a Lego brick you can pipe other commands into —
the heart of command-line automation. Inspired by Simon Willison's `llm` tool.

Run it like:
    uv run demos/reserve/llm.py "Explain a Python list in one sentence"
    cat report.txt | uv run demos/reserve/llm.py "Summarize this in 3 bullets"
    git log --oneline -10 | uv run demos/reserve/llm.py "Write release notes"
    uv run demos/reserve/llm.py "Hello" -m claude-opus-4-8

Needs: OPENAI_API_KEY (default model) or ANTHROPIC_API_KEY (for -m claude-*)
in the repo-root .env file.
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]


def require_key(name: str, where: str) -> str:
    """Load .env from the repo root, fall back to the environment, or explain the fix."""
    load_dotenv(REPO_ROOT / ".env")
    key = os.environ.get(name)
    if not key:
        print(f"No {name} found.")
        print(f"1) Get a key at {where}")
        print(f"2) Add this line to {REPO_ROOT / '.env'}:  {name}=your-key-here")
        sys.exit(1)
    return key


def ask_openai(prompt: str, system: str, model: str) -> str:
    from openai import OpenAI

    require_key("OPENAI_API_KEY", "https://platform.openai.com/api-keys")
    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def ask_anthropic(prompt: str, system: str, model: str) -> str:
    import anthropic

    require_key("ANTHROPIC_API_KEY", "https://console.anthropic.com/settings/keys")
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=16000,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    # Claude replies with a list of content blocks; keep only the text ones.
    return "".join(block.text for block in response.content if block.type == "text")


def ask(prompt: str, system: str, model: str) -> str:
    # Provider is picked from the model name: claude-* goes to Anthropic,
    # everything else to OpenAI. Simple and good enough for a personal tool.
    if "claude" in model:
        return ask_anthropic(prompt, system, model)
    return ask_openai(prompt, system, model)


def read_stdin() -> str:
    # isatty() is True when a human is at the keyboard and nothing was piped in.
    if sys.stdin.isatty():
        return ""
    return sys.stdin.read().strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a prompt (and/or piped text) to an AI model.")
    parser.add_argument("prompt", nargs="?", default="", help="Your question or instruction.")
    parser.add_argument("-m", "--model", default="gpt-5.6-luna",
                        help="Model (default: gpt-5.6-luna; claude-opus-4-8 for Anthropic)")
    parser.add_argument("--system", default="You are a helpful assistant. Be concise.",
                        help="System prompt / persona.")
    args = parser.parse_args()

    piped = read_stdin()
    if piped and args.prompt:
        full_prompt = f"{args.prompt}\n\n---\n{piped}"
    else:
        full_prompt = args.prompt or piped

    if not full_prompt:
        parser.error("give me a prompt as an argument, or pipe some text in on stdin")

    print(ask(full_prompt, args.system, args.model))


if __name__ == "__main__":
    main()
