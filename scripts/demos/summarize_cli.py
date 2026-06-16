# /// script
# requires-python = ">=3.12"
# dependencies = ["anthropic", "openai"]
# ///
"""
summarize_cli.py — Summarize content with AI

    uv run summarize_cli.py "content"

"""
import os
import sys


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

def summarize(content):
    summary_sys_msg = "You summarize content in bullet points"
    prompt_summary = f"Summarize this: {content}"
    return ask(prompt_summary, summary_sys_msg)
    

def main():
    content = sys.argv[1]
    print(content)
    print("Summarizing:")
    summarized_content = summarize(content)
    print(f"Summarized content:\n\n {summarized_content}")

if __name__ == "__main__":
    main()
