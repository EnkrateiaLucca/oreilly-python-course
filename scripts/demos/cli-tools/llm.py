# /// script
# requires-python = ">=3.12"
# dependencies = ["openai", "anthropic"]
# ///
"""A tiny `llm`-style command: send text to an AI model from your terminal.

Automation category: CLI tools.

Input   -> a prompt as an argument AND/OR text piped in on stdin
Process -> send it to OpenAI (default) or Anthropic and stream nothing fancy back
Output  -> the model's reply printed to stdout

Inspired by Simon Willison's `llm` tool (https://github.com/simonw/llm), but
stripped down to the one idea that makes it powerful: it reads from stdin, so it
becomes a Lego brick you can pipe other commands into. That is the heart of
command-line automation -- small tools that compose.

Run it like:
    # ask a question directly
    uv run scripts/demos/cli-tools/llm.py "Explain a Python list in one sentence"

    # pipe a file in and ask a question ABOUT it
    cat report.txt | uv run scripts/demos/cli-tools/llm.py "Summarize this in 3 bullets"

    # chain it after another command
    git log --oneline -10 | uv run scripts/demos/cli-tools/llm.py "Write release notes"

    # give it a persona with --system, or switch models with -m
    uv run scripts/demos/cli-tools/llm.py "Rewrite politely" --system "You are a terse editor"
    uv run scripts/demos/cli-tools/llm.py "Hello" -m claude-sonnet-4-6

Needs: OPENAI_API_KEY (default) or ANTHROPIC_API_KEY (for -m claude-*) in your environment.
"""

import argparse
import sys


def ask_openai(prompt: str, system: str, model: str) -> str:
    from openai import OpenAI

    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


def ask_anthropic(prompt: str, system: str, model: str) -> str:
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        system=system,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
    )
    return response.content[0].text


def ask(prompt: str, system: str, model: str) -> str:
    # We pick the provider from the model name: anything with "claude" goes to
    # Anthropic, everything else goes to OpenAI. This is the same trick the
    # course's scripts/lib/ai_tools.py uses.
    if "claude" in model:
        return ask_anthropic(prompt, system, model)
    return ask_openai(prompt, system, model)


def read_stdin() -> str:
    # sys.stdin.isatty() is True when nobody piped anything in (a human is at the
    # keyboard). When it's False, something was piped to us -- so we read it.
    if sys.stdin.isatty():
        return ""
    return sys.stdin.read().strip()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send a prompt (and/or piped text) to an AI model.")
    parser.add_argument("prompt", nargs="?", default="", help="Your question or instruction.")
    parser.add_argument("-m", "--model", default="gpt-5-mini", help="Model name (default: gpt-5-mini; use claude-* for Anthropic).")
    parser.add_argument("--system", default="You are a helpful assistant. Be concise.", help="System prompt / persona.")
    args = parser.parse_args()

    piped = read_stdin()

    # Combine the typed prompt and the piped text. Either one alone is fine.
    if piped and args.prompt:
        full_prompt = f"{args.prompt}\n\n---\n{piped}"
    else:
        full_prompt = args.prompt or piped

    if not full_prompt:
        parser.error("Give me a prompt as an argument, or pipe some text in on stdin.")

    print(ask(full_prompt, args.system, args.model))
