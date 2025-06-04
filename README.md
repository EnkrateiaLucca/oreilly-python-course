# O'Reilly Live Training - Automate Tasks with Python + AI 

## Quick Setup

### 1. Install UV
**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone and Setup Project

**Linux/macOS:**
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

**Windows (PowerShell):**
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

### 3. Start Jupyter Lab
```bash
# Make sure you're in the project directory
jupyter lab
```

## API Setup

### Get your API keys:
1. OpenAI [API key](https://platform.openai.com/)
2. Anthropic [API key](https://docs.anthropic.com/en/docs/get-started)

### Setup your .env file
Change the `.env.example` file to `.env` and add your API keys:

```bash
OPENAI_API_KEY=<your openai api key>
ANTHROPIC_API_KEY=<your claude api key>
```

## What's Included
Dependencies installed:
- **AI Libraries:** openai, anthropic, ollama
- **Data Science:** pandas, matplotlib
- **Web Scraping:** requests, beautifulsoup4, playwright
- **Jupyter:** jupyterlab, ipykernel, ipywidgets
