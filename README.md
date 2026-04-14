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

**Automated Setup (Recommended):**
```powershell
# 1. Clone the repository
git clone https://github.com/EnkrateiaLucca/oreilly-python-course
cd oreilly-python-course

# 2. Run the automated setup script
.\setup-windows.ps1
```

**Manual Setup:**
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

**Having Issues?** Run the diagnostic tool:
```powershell
.\diagnose-setup.ps1
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

# Course Notebooks

This directory contains all the Jupyter notebooks for the O'Reilly Live Training course organized into logical sections.

## Structure

### 📚 notebooks/01-python-fundamentals/
Core Python concepts and syntax:
- **01-python-basics.ipynb** – Python basics: numbers, strings, variables, operators
- **02-working-with-data.ipynb** – Lists, dictionaries, file I/O, CSV handling
- **03-packages-apis.ipynb** – Using libraries and working with APIs
- **file.txt** – Sample text file for file operations
- **places_to_go.csv** – Example CSV data for exercises

### 🤖 02-ai-apis/
Working with AI services:
- **01-ai-apis-overview.ipynb** - Introduction to AI APIs
- **02-ai-tools-hands-on.ipynb** - Practical AI tool usage

### ⚙️ 03-automation-projects/
Real-world automation projects:
- **01-file-management-automation.ipynb** - Organizing and managing files
- **02-data-extraction-with-ai.ipynb** - Extracting data using LLMs
- **03-web-data-extraction.ipynb** - Web scraping and data collection
- **04-data-analysis-automation.ipynb** - Automated data analysis
- **05-presentation-automation.ipynb** - Generating slides automatically
- **06-browser-automation.ipynb** - Controlling web browsers
- **07-workflow-automation.ipynb** - Building automation workflows
- **08-email-assistant.ipynb** - Email automation and processing
- **09-ai-scheduler-agent.ipynb** - Intelligent scheduling systems
- **10-receipt-data-extraction.ipynb** - Processing receipts and invoices
- **11-custom-automation-scripts.ipynb** - Building your own scripts
- **12-practical-examples.ipynb** - Additional real-world examples

### 📝 04-exercises/
Practice problems and solutions:
- **01-data-types-and-variables.ipynb** - Basic Python practice
- **02-functions.ipynb** - Function creation exercises
- **03-conditionals-and-files.ipynb** - Logic and file handling
- **04-day1-recap.ipynb** - Summary and review

### 📁 assets/
Supporting files, images, sample data, and resources used throughout the course.

## Getting Started

1. Navigate to `01-python-fundamentals/` if you're new to Python
2. Work through notebooks in numerical order within each section
3. Use `04-exercises/` to practice what you've learned
4. Move to `02-ai-apis/` and `03-automation-projects/` for advanced topics

## Tips

- Each notebook is self-contained but builds on previous concepts
- Sample data and resources are in the `assets/` folder
- Run notebooks in order for the best learning experience
