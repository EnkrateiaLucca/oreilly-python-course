# Complete Beginner Setup Guide

## 🍎 Mac Setup (Complete from scratch)

**Step 1: Install Homebrew (package manager)**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Step 2: Install Git**
```bash
brew install git
```

**Step 3: Fix permissions and install UV**
```bash
chmod +w ~/.bash_profile ~/.zshrc
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.zshrc
```

**Step 4: Setup the course**
```bash
git clone https://github.com/EnkrateiaLucca/oreilly-python-course
cd oreilly-python-course
uv venv
source .venv/bin/activate
uv pip install jupyterlab ipykernel openai pandas anthropic ollama requests beautifulsoup4 matplotlib ipywidgets playwright
python -m ipykernel install --user --name=oreilly-python-ai --display-name "O'Reilly Python AI"
playwright install
echo "✅ Setup complete! Run: jupyter lab"
```

---

## 🪟 Windows Setup (Complete from scratch)

**Step 1: Install Git (Download and run installer)**
- Go to: https://git-scm.com/download/win
- Download and install with default settings

**Step 2: Open PowerShell as Administrator and install UV**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Step 3: Close and reopen PowerShell (normal user), then setup course**
```powershell
git clone https://github.com/EnkrateiaLucca/oreilly-python-course
cd oreilly-python-course
uv venv
.venv\Scripts\activate
uv pip install jupyterlab ipykernel openai pandas anthropic ollama requests beautifulsoup4 matplotlib ipywidgets playwright
python -m ipykernel install --user --name=oreilly-python-ai --display-name "O'Reilly Python AI"
playwright install
Write-Output "✅ Setup complete! Run: jupyter lab"
```

---

## 🚀 Start Working
After setup, always run:

**Mac/Linux:**
```bash
cd oreilly-python-course
source .venv/bin/activate
jupyter lab
```

**Windows:**
```powershell
cd oreilly-python-course
.venv\Scripts\activate
jupyter lab
```

---

## 🔧 Troubleshooting

### Mac Issues:
- If Homebrew install fails: Try running `xcode-select --install` first
- If permission denied: Run `chmod +w ~/.bash_profile ~/.zshrc`
- If uv not found: Restart terminal or run `source ~/.zshrc`

### Windows Issues:
- If PowerShell blocked: Run as Administrator and set execution policy
- If Git not found: Restart PowerShell after Git installation
- If uv not found: Close and reopen PowerShell

### Common Issues:
- If packages fail to install: Make sure virtual environment is activated
- If Jupyter won't start: Run `jupyter lab --generate-config` then try again
- If kernel not found in Jupyter: Re-run the `python -m ipykernel install` command

---

## 📚 What You'll Have After Setup

✅ **Python Environment**: Isolated virtual environment with UV  
✅ **Jupyter Lab**: Interactive notebook environment  
✅ **AI Libraries**: OpenAI, Anthropic, Ollama for AI integration  
✅ **Data Science**: Pandas, Matplotlib for data analysis  
✅ **Web Automation**: Playwright, BeautifulSoup for web scraping  
✅ **Course Materials**: All notebooks organized and ready to use

---

## 🎯 Next Steps

1. **Open Jupyter Lab**: Run `jupyter lab` in your activated environment
2. **Navigate to**: `notebooks/01-python-fundamentals/` to start learning
3. **Follow the progression**: Fundamentals → AI APIs → Automation Projects → Exercises
4. **Practice**: Work through exercises to solidify your learning

Happy coding! 🚀