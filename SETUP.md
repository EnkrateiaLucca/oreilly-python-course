# Setup — one install, five minutes

You do **not** need to install Python. You do **not** need to know what a virtual
environment is. One tool — `uv` — handles everything, including downloading Python
itself the first time you run a script.

## Step 1 — Install uv

**Mac** — open Terminal (⌘-space, type "Terminal"), paste, press Enter:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows** — open PowerShell (Start menu, type "PowerShell"), paste, press Enter:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Close the terminal, open a new one, and check it worked:

```bash
uv --version
```

Any version number = you're done with the hard part.

## Step 2 — Get the course folder

**Easiest (no git needed):** on the [repo page](https://github.com/EnkrateiaLucca/oreilly-python-course),
click the green **Code** button → **Download ZIP** → unzip it somewhere you can find
(Desktop is fine).

**If you have git:**

```bash
git clone https://github.com/EnkrateiaLucca/oreilly-python-course
```

## Step 3 — Run your first script

In your terminal, go into the folder and run lesson 1:

```bash
cd oreilly-python-course        # or wherever you unzipped it
uv run lessons/01_first_run.py
```

The very first run takes ~30 seconds (uv quietly sets everything up). After that,
scripts start instantly. If you see the lesson's output — **setup is complete.**

## Step 4 — API keys (needed from lesson 07 onward, not before)

The AI-powered scripts talk to OpenAI and/or Anthropic. Keys live in a `.env` file
that stays on your machine.

1. Copy the example file:
   - Mac: `cp .env.example .env`
   - Windows: `copy .env.example .env`
2. Get a key from [OpenAI](https://platform.openai.com/) and/or
   [Anthropic](https://console.anthropic.com/) (either one is enough to follow the course).
3. Open `.env` in any text editor and paste your key(s) after the `=`.

**Never** paste keys into scripts or chats. Scripts read them from `.env` automatically.

## Optional — local AI (no key, no cloud)

Two demos can run AI entirely on your machine via [Ollama](https://ollama.com):
install it, then `ollama pull gemma4`. Skip this freely — every demo has a cloud path.

## Editor

Use [VS Code](https://code.visualstudio.com/) as a plain text editor with a built-in
terminal (Terminal menu → New Terminal). You don't need any extensions, and you never
need to pick an "interpreter" — `uv run` ignores all of that.

## If something goes wrong

| Symptom | Fix |
|---|---|
| `uv: command not found` / not recognized | Close the terminal and open a new one (PATH updates on restart). |
| Windows says "running scripts is disabled" | Use the exact PowerShell command from Step 1 — the `-ExecutionPolicy ByPass` part handles it. |
| Corporate laptop blocks the install | Use the cloud fallback below. |
| A script says an API key is missing | Do Step 4 — the message tells you exactly which key. |

## Cloud fallback (nothing installable at all)

Click the **Open in GitHub Codespaces** badge in the README — you get this exact
folder with uv preinstalled, in your browser, in ~2 minutes. (Codespaces' free tier
is far more than this course needs.)
