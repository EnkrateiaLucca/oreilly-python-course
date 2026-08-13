# Build an automation for MY machine — macOS

Paste this whole prompt into a chatbot (Claude, ChatGPT) **or** hand it to a coding
agent (Claude Code, run from the folder where you keep your tools). Fill in the
ticket first. The machine details are already correct for a Mac — don't edit them.

---

```
You are helping a beginner build a personal automation on macOS, following a
safety-first process. Build exactly what the ticket says — nothing more.

<my ticket>
TASK:       ...
TRIGGER:    ...
TOUCHES:    ...
MUST NEVER: ...
DONE MEANS: ...
</my ticket>

<my machine — macOS, do not change these assumptions>
- Shell: zsh. Aliases go in ~/.zshrc, one line, then `source ~/.zshrc`.
- Python: NOT installed system-wide and that's fine — everything runs through uv.
  uv lives at ~/.local/bin/uv. Scripts run with: uv run script.py
- My tools folder: ~/tools (create it if needed; all scripts live there).
- Scheduler: launchd. Scheduled jobs are .plist files in ~/Library/LaunchAgents/,
  loaded with `launchctl load ~/Library/LaunchAgents/<name>.plist`.
  IMPORTANT: the plist's ProgramArguments must use the FULL uv path
  (/Users/<me>/.local/bin/uv) because launchd doesn't read my shell profile.
- Secrets: API keys live in ~/tools/.env — scripts load them with python-dotenv.
  Never put a key inside a script.
</my machine>

Requirements for the script itself:
1. One Python file with uv inline metadata (PEP 723): a `# /// script` header
   declaring requires-python ">=3.12" and every dependency.
2. Only packages that really exist on PyPI — list them all in the header.
3. Simple code: small functions, no classes, readable by a beginner.
4. If it moves/changes/deletes/sends ANYTHING: dry-run by default, act only
   with --apply. argparse so --help explains it. Friendly errors, never a
   raw traceback. Respect every MUST NEVER line in code.
5. End by printing a one-line summary matching DONE MEANS.

Deliver, in this order:
A. The script.
B. A plain-English walkthrough: everything it reads, writes, or sends
   (I will check this against the code — this is my Run Gate).
C. The exact commands to test it: --help, then the dry run, then --apply
   on a practice copy.
D. The one-line alias for ~/.zshrc.
E. Only if my TRIGGER is scheduled: the complete .plist (with the full uv
   path), where to save it, the launchctl load command, and how to trigger
   it once right now to verify (launchctl start <label>).

If you are a coding agent with file access: create the script in ~/tools,
run the --help and dry-run yourself and show me the output — but do NOT run
--apply, do NOT edit ~/.zshrc, and do NOT load any plist. Those three I do
myself, after reading your walkthrough.
```

---

**After you get the result:** don't skip the Run Gate (`run-gate.md`) — check the
walkthrough against the code, check every package on pypi.org, dry-run first.
