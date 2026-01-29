# Windows Quick Start - 5 Minute Setup

**New to this?** See [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for detailed instructions.

## Prerequisites

✅ Python 3.13+ installed → [Download](https://www.python.org/downloads/)
✅ Git installed → [Download](https://git-scm.com/download/win)
✅ Internet connection

## Setup Steps

### Option A: Automated (Recommended)

Open PowerShell and run:

```powershell
# Clone the project
git clone https://github.com/EnkrateiaLucca/oreilly-python-course
cd oreilly-python-course

# Run setup script (handles everything)
.\setup-windows.ps1
```

**That's it!** The script will install UV, sync packages, and set everything up.

---

### Option B: Manual

```powershell
# 1. Install UV
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. Close PowerShell and open a NEW one

# 3. Clone project
git clone https://github.com/EnkrateiaLucca/oreilly-python-course
cd oreilly-python-course

# 4. Install packages (takes 5-10 min)
uv sync

# 5. Setup Jupyter
uv run ipython kernel install --user --env VIRTUAL_ENV "$PWD\.venv" --name=oreilly-automate-py

# 6. Install browsers (optional)
uv run playwright install
```

---

## Start Learning

```powershell
uv run --with jupyter jupyter lab
```

Opens in your browser automatically!

---

## Setup API Keys

1. Copy `.env.example` → `.env`
2. Get keys:
   - OpenAI: https://platform.openai.com/
   - Anthropic: https://console.anthropic.com/
3. Add them to `.env`

---

## Common Issues

### "Command not found" errors
→ Close terminal and open a **NEW** one

### UV won't install
→ Run PowerShell **as Administrator**
→ Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Antivirus blocking
→ Temporarily disable during setup
→ Or add project folder to exceptions

### Setup taking too long
→ Normal! Package installation takes 5-10 minutes
→ See progress messages to confirm it's working

### Still stuck?
```powershell
.\diagnose-setup.ps1  # Identifies issues
```

---

## Daily Usage

Start working:
```powershell
cd oreilly-python-course
uv run --with jupyter jupyter lab
```

That's it!

---

**Need more help?** → [WINDOWS_SETUP.md](WINDOWS_SETUP.md)
**Report issues** → https://github.com/EnkrateiaLucca/oreilly-python-course/issues
