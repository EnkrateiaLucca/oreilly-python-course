# Prompt

The "R" in the SCRIPT loop. Paste this — ticket included — into Claude, ChatGPT,
or any capable AI. The constraints below are what make the result *safe to inspect
and boring to run*, which is exactly what you want.

## The prompt

```
Write me a complete, runnable, single-file Python script.

<my ticket>
TASK: ...
TRIGGER: ...
TOUCHES: ...
MUST NEVER: ...
DONE MEANS: ...
</my ticket>

Requirements — follow all of them:
1. One file, with uv inline script metadata at the top (PEP 723):
   # /// script
   # requires-python = ">=3.12"
   # dependencies = ["..."]
   # ///
   so I can run it with: uv run script.py
2. Only use packages that really exist on PyPI. List every dependency in the header.
3. Keep it simple: small functions, no classes, no clever tricks. I need to be able
   to READ this script.
4. If the script moves, changes, deletes, or sends ANYTHING: dry-run by default
   (print what it would do), and only act with an --apply flag.
5. Use argparse so --help explains the script.
6. Friendly errors: if something is missing (a folder, an API key), print a short
   plain-English message telling me how to fix it — never a raw traceback.
7. Respect every line of MUST NEVER, in code, not just in comments.
8. At the end, print a one-line summary of what was done, matching DONE MEANS.
```

## If the script calls an AI API

Add one of these blocks so the AI uses the current API correctly instead of guessing:

```
Use the Anthropic Python SDK:
  from anthropic import Anthropic
  client = Anthropic()  # reads ANTHROPIC_API_KEY from the environment
  response = client.messages.create(
      model="claude-opus-4-8", max_tokens=16000,
      messages=[{"role": "user", "content": prompt}])
  text = "".join(b.text for b in response.content if b.type == "text")
```

```
Use the OpenAI Python SDK with model "gpt-5.6-luna".
```

*(Showing the AI how to call an API — instead of letting it guess — is one of the
highest-leverage prompting habits there is.)*

## After you get the code

Do not run it. Go to the Run Gate: `run-gate.md`. That's the "I" step.

Once it passes and proves out, finish it as a *reusable tool* — clear inputs,
clear outputs, safe defaults, a written usage contract — and, if it's worth it,
wrap it as an agent skill. See `tool-to-skill.md`. The script is cheap; the
reusable capability is the asset.

## Iterating

- Wrong result? Improve the **ticket**, not just the chat — then regenerate.
- Long chats make AIs dumber. When a fix drags past 2-3 turns, start a **fresh chat**
  with the improved ticket + the current script pasted in.
- Sometimes the right move is to throw the script away and regenerate. They're cheap.

## How to read the verdict

_(Placeholder — this prompt produces a script, not a verdict. Don't run it: take
the output straight to the Run Gate (`run-gate.md`), then prove it against DONE
MEANS.)_
