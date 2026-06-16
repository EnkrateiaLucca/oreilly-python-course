# O'Reilly Live Training - Automate Tasks with Python + AI 

## Quickest Setup: GitHub Codespaces (Recommended)

No local installation needed! Click the button below to launch a fully configured environment in your browser:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/EnkrateiaLucca/oreilly-python-course)

> **Note:** Codespaces usage is billed to **your own** GitHub account. GitHub Free includes 120 core-hours/month — more than enough for this course.

After the Codespace launches (takes ~2 minutes), just:
1. Copy `.env.example` to `.env` and add your API keys:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` with your OpenAI and/or Anthropic API keys
3. Start Jupyter Lab:
   ```bash
   uv run --with jupyter jupyter lab
   ```

---

## Local Setup

### 1. Install UV
**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**

> **🪟 Windows Users:** For complete beginners or if you encounter any issues, see **[WINDOWS_SETUP.md](WINDOWS_SETUP.md)** for a comprehensive step-by-step guide with troubleshooting.

**Setup:**
```powershell
# Install UV first
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Then run these commands
git clone https://github.com/EnkrateiaLucca/oreilly-python-course
cd oreilly-python-course
uv sync
uv run ipython kernel install --user --env VIRTUAL_ENV "$PWD\.venv" --name=oreilly-automate-py
uv run playwright install
```


### 2. Clone and Setup Project (Linux/macOS)

```bash
git clone https://github.com/EnkrateiaLucca/oreilly-python-course
cd oreilly-python-course
uv sync
source .venv/bin/activate
uv run ipython kernel install --user --env VIRTUAL_ENV "$PWD\.venv" --name=oreilly-automate-py
playwright install
echo "✅ Setup complete! To execute the jupyter environment for the interactive notebooks run:"
uv run --with jupyter jupyter lab
```

### 3. Start Jupyter Lab
```bash
# Make sure you're in the project directory
uv run --with jupyter jupyter lab
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

# Course Content

This is a **two-day live training**. The course material is organized by day under `notebooks/`, with supporting slides, scripts, and assets in their own top-level folders.

## Notebook Structure

### 📅 Day 1 — `notebooks/day-1/`
Python fundamentals, then a first look at AI APIs:
- **01-python-basics.ipynb** – Data types, variables, f-strings, functions, lists, loops, dictionaries, comparisons, and conditionals — taught with practical, real-world examples
- **02-working-with-data.ipynb** – Lists, dictionaries, file I/O, CSV, pandas, and using AI to summarize/categorize data
- **03-packages-apis.ipynb** – Importing libraries, custom modules, calling external APIs, and **working with AI APIs** (OpenAI, Anthropic, and local Ollama models; plus image generation and audio transcription)

### 📅 Day 2 — `notebooks/day-2/`

**`03-automation-projects/`** — real-world automation:
- **01-file-management-automation.ipynb** – Extract invoice data and organize files with AI
- **02-data-extraction.ipynb** – Structured receipt/data extraction to JSON (OpenAI, Claude, and local models)
- **03-data-analysis-and-automation.ipynb** – Download data, scrape the web, and analyze with pandas

**`04-exercises/`** — practice problems:
- **01-data-types-and-variables.ipynb** – Basic Python practice
- **02-functions.ipynb** – Function creation exercises
- **03-conditionals-and-files.ipynb** – Logic and file handling
- **04-day1-recap.ipynb** – Day 1 summary and review
- **05-tutorial_learning_python_with_pdfs.ipynb** – Learning Python by working with PDFs

**`05-how-to-learn-python/`** — using AI to learn the language:
- **how-to-learn-python.ipynb** – Strategies for learning Python with AI
- **learn-python-talking-to-ai.ipynb** – Using an AI model as a personal Python tutor
- **learn-python-with-solveit.ipynb** – A guided tour of the `solveit` toolkit: dialogue-based learning, Pólya's loop, interactive quizzes, and turning a notebook into an AI tutor

## Other Folders

- **`presentation/`** – The course slide deck (`presentation.html`, a remark.js presentation)
- **`scripts/`** – Standalone automation scripts and shared helpers. `scripts/lib/` holds modules the notebooks import (`ai_tools.py`, and `solveit.py` — a teachable AI-tutor toolkit). `scripts/ask.py` is a one-liner CLI tutor (`uv run scripts/ask.py "your question"`). `scripts/archive/` holds older demos
- **`assets/`** – Sample data, PDFs, spreadsheets, and other resources used by the notebooks

## Getting Started

1. Complete the setup above (Codespaces or local), add your API keys, and launch Jupyter Lab
2. Start with **`notebooks/day-1/`** and work through the notebooks in order
3. Move on to **`notebooks/day-2/`** for the automation projects and exercises

## Tips

- Select the **`oreilly-automate-py`** kernel so every notebook uses the same environment
- Notebooks build on each other — run them in order within each day
- AI cells need valid API keys in `.env`; cells using local models need [Ollama](https://ollama.com/download) installed and running
- Sample data lives in `assets/`, referenced from the notebooks via relative paths
