# Build an automation for MY machine — Windows

Paste this whole prompt into a chatbot (Claude, ChatGPT) **or** hand it to a coding
agent (Claude Code, run from the folder where you keep your tools). Fill in the
ticket first. The machine details are already correct for Windows — don't edit them.

---

```
You are helping a beginner build a personal automation on Windows, following a
safety-first process. Build exactly what the ticket says — nothing more.

<my ticket>
TASK:       ...
TRIGGER:    ...
TOUCHES:    ...
MUST NEVER: ...
DONE MEANS: ...
</my ticket>

<my machine — Windows, do not change these assumptions>
- Shell: PowerShell. "Aliases" are functions in my profile: open it with
  `notepad $PROFILE` (create if missing), add
  `function toolname { uv run $HOME\tools\script.py }`, reopen PowerShell.
- Python: NOT installed system-wide and that's fine — everything runs through uv.
  Scripts run with: uv run script.py
- My tools folder: $HOME\tools (create it if needed; all scripts live there).
- Scheduler: Windows Task Scheduler via one schtasks command, e.g.:
  schtasks /create /tn "MyTool" /tr "uv run %USERPROFILE%\tools\script.py --apply"
    /sc daily /st 07:30
  IMPORTANT: if the task doesn't find uv, use the full path
  %USERPROFILE%\.local\bin\uv.exe in /tr.
- Secrets: API keys live in $HOME\tools\.env — scripts load them with
  python-dotenv. Never put a key inside a script.
- Paths in Python: always pathlib (it handles Windows backslashes for me).
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
C. The exact PowerShell commands to test it: --help, then the dry run, then
   --apply on a practice copy.
D. The profile function for $PROFILE.
E. Only if my TRIGGER is scheduled: the complete schtasks /create command,
   plus `schtasks /run /tn "<name>"` to trigger it once right now to verify.

If you are a coding agent with file access: create the script in $HOME\tools,
run the --help and dry-run yourself and show me the output — but do NOT run
--apply, do NOT edit my $PROFILE, and do NOT create any scheduled task. Those
three I do myself, after reading your walkthrough.
```

---

**After you get the result:** don't skip the Run Gate (`run-gate.md`) — check the
walkthrough against the code, check every package on pypi.org, dry-run first.
