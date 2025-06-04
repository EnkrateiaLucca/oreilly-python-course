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

### 2. One-Command Setup

**Clone the Repo**

- `git clone https://github.com/EnkrateiaLucca/oreilly-python-course`

**Linux/macOS:**
```bash
uv sync --dev && \
uv run python -m ipykernel install --user --name=oreilly-python-ai --display-name "O'Reilly Python AI" && \
uv run playwright install && \
echo "✅ Setup complete! Run: uv run jupyter lab"
```

**Windows (PowerShell):**
```powershell
uv sync --dev; uv run python -m ipykernel install --user --name=oreilly-python-ai --display-name "O'Reilly Python AI"; uv run playwright install; Write-Output "✅ Setup complete! Run: uv run jupyter lab"
```

### 3. Start Jupyter Lab
```bash
uv run jupyter lab
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
All dependencies are managed in `pyproject.toml`:
- **AI Libraries:** openai, anthropic, ollama
- **Data Science:** pandas, matplotlib
- **Web Scraping:** requests, beautifulsoup4, playwright
- **Jupyter:** jupyterlab, ipykernel, ipywidgets

<!-- 1. [](notebooks/9.0-building-email-assistant.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly-python-course/blob/main/notebooks/9.0-building-email-assistant.ipynb) -->
