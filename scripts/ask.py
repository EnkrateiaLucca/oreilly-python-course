# /// script
# requires-python = ">=3.12"
# dependencies = ["anthropic", "openai"]
# ///
"""
ask.py — a one-liner SolveIt question from the terminal.

    uv run ask.py "What is a Python dictionary?"
    uv run ask.py --tutor "Explain f-strings to a beginner"

Auto-detects ANTHROPIC_API_KEY or OPENAI_API_KEY. Override the model with
SOLVEIT_MODEL. The companion of solveit.py for when you're not in a notebook.
"""
import os
import sys

TUTOR = ("You are a patient Python tutor for a beginner. Keep it short, use a "
         "tiny runnable example, explain each line plainly, end with a small "
         "next step.")


def ask(prompt: str, system: str | None = None) -> str:
    model = os.environ.get("SOLVEIT_MODEL")
    if os.environ.get("ANTHROPIC_API_KEY"):
        import anthropic
        client = anthropic.Anthropic()
        r = client.messages.create(
            model=model or "claude-sonnet-4-6",
            system=system or "You are a helpful assistant.",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
        )
        return r.content[0].text
    if os.environ.get("OPENAI_API_KEY"):
        from openai import OpenAI
        client = OpenAI()
        msgs = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": prompt}]
        r = client.chat.completions.create(model=model or "gpt-5.4-mini", messages=msgs)
        return r.choices[0].message.content
    sys.exit("No API key found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY.")


def main():
    args = sys.argv[1:]
    system = None
    if args and args[0] == "--tutor":
        system = TUTOR
        args = args[1:]
    if not args:
        sys.exit('Usage: uv run ask.py [--tutor] "your question"')
    print(ask(" ".join(args), system=system))


if __name__ == "__main__":
    main()
