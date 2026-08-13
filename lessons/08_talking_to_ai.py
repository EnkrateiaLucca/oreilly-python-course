# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "openai",
#     "anthropic",
#     "ollama",
#     "python-dotenv",
# ]
# ///
"""
LESSON 08 — Talking to AI (the same dance, three counters)
==========================================================

Lesson 07's API dance — build a request, send it, read the answer —
works unchanged for AI. The only news: AI counters check ID. That ID is
an API key, a long secret string that lives in a file called .env at
the repo root (copy .env.example and paste your keys in).

We ask the SAME question at three counters: OpenAI, Anthropic, and a
local model via Ollama running on your own machine — no key, no
internet, free.

No keys yet? Run me anyway — I'll show you exactly what WOULD happen
and how to get set up. Nothing will crash.

After this lesson you can READ:  .env / API keys  ·  client objects  ·  the messages=[...] pattern  ·  try/except

Run me with:
    uv run lessons/08_talking_to_ai.py
"""

# 🗣 EXPLAIN IT (before running): in one sentence — what is this script FOR?

import os
from pathlib import Path
from dotenv import load_dotenv

# ── loading keys: the standard block you'll see in every demo ────────────
# load_dotenv reads KEY=value lines from .env into the environment;
# os.environ.get looks them up (returning None, not crashing, if absent).
# Why you care: this exact block opens every keyed script in this course —
# and "reads a .env" is a blast-radius fact worth noticing (secrets!).
REPO_ROOT = Path(__file__).parent.parent
load_dotenv(REPO_ROOT / ".env")

openai_key = os.environ.get("OPENAI_API_KEY") or None      # "" counts as missing
anthropic_key = os.environ.get("ANTHROPIC_API_KEY") or None

QUESTION = "In one short sentence: why is it worth READING a script before running it?"


def ask_openai(prompt):
    """The question, asked at OpenAI's counter."""
    from openai import OpenAI
    client = OpenAI()   # the 'client' is your open line to the service
    response = client.chat.completions.create(
        model="gpt-5.6-luna",
        messages=[{"role": "user", "content": prompt}],
        # ^ messages is a LIST of DICTIONARIES (lessons 02's vocabulary!)
        #   — the universal shape of AI conversations.
    )
    return response.choices[0].message.content


def ask_anthropic(prompt):
    """The same question at Anthropic's counter — same dance, new steps."""
    import anthropic
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=16000,   # an upper limit on the answer's length
        messages=[{"role": "user", "content": prompt}],
    )
    # Anthropic answers in typed blocks; we keep the text ones.
    return "".join(block.text for block in message.content if block.type == "text")


def ask_ollama(prompt):
    """And at the counter INSIDE your computer: local, free, keyless."""
    import ollama
    response = ollama.chat(model="gemma4",
                           messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]


# ── PREDICT: with no keys in place, does this script crash or cope? ──
if not openai_key and not anthropic_key:
    print("No API keys found — here's the dress rehearsal instead.\n")
    print("With keys in place, this script would:")
    print(f'  1. Send "{QUESTION}"')
    print("     to OpenAI's gpt-5.6-luna and print its one-line answer.")
    print("  2. Send the same question to Anthropic's claude-opus-4-8.")
    print("  3. Ask a local gemma4 model via Ollama (that one needs no key —")
    print("     it runs after setup either way).")
    print("\nThe 3-line fix:")
    print("  1. Get keys at platform.openai.com and console.anthropic.com")
    print(f"  2. Copy {REPO_ROOT / '.env.example'} to {REPO_ROOT / '.env'}")
    print("  3. Paste your keys inside and rerun this script. That's it!")
    raise SystemExit(0)   # a graceful exit — expected situation, not an error

print(f'Asking three AIs: "{QUESTION}"\n')

# ── PREDICT: will the two cloud models give the SAME sentence? ──
# (No — models are like colleagues, not calculators. Same question,
#  different phrasing every time. Discernment is YOUR job.)
for name, key, ask in [("OpenAI (gpt-5.6-luna)", openai_key, ask_openai),
                       ("Anthropic (claude-opus-4-8)", anthropic_key, ask_anthropic)]:
    if key:
        print(f"── {name} says ──")
        print(f"  {ask(QUESTION)}\n")
    else:
        print(f"── {name}: no key found in .env — skipped. ──\n")

# try/except — lesson 06's safety net, out in the wild: attempt the
# local call, and if Ollama isn't running, do plan B instead of dying.
# This is how good scripts stay friendly when the world doesn't cooperate.
print("── Local model via Ollama (gemma4) ──")
try:
    print(f"  {ask_ollama(QUESTION)}\n")
except Exception:
    print("  Ollama isn't running here — that's fine, skip it! (To try local")
    print("  AI later: install from ollama.com, then run: ollama pull gemma4)\n")

print("Same question, three counters, one pattern: client -> messages -> answer.")
print("You can now read ANY 'call the AI' block. Lesson 09: the payoff.")

# ✏️ TRY IT:
#   1. Change QUESTION to something from your actual job and rerun.
#   2. In ask_anthropic, drop max_tokens to 50 and see the answer clipped.
#   3. Rename .env to .env.backup and rerun — watch the graceful path.
#      (Rename it back!) Friendly failure is a feature you should DEMAND
#      from AI-generated scripts.
