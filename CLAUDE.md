# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an O'Reilly Live Training course repository for "Automate Tasks with Python + AI". It's an educational project focused on teaching Python automation using AI APIs, particularly OpenAI and Anthropic APIs.

## Development Setup

The project uses `uv` for dependency management. To set up the development environment:

```bash
uv sync
uv run ipython kernel install --user --env VIRTUAL_ENV $(pwd)/.venv --name=oreilly-automate-py
playwright install
```

## Common Commands

### Running Jupyter Lab
```bash
uv run --with jupyter jupyter lab
```

### Running Python scripts
```bash
uv run python main.py
uv run python scripts/<script_name>.py
```

### Installing Playwright (for web automation)
```bash
playwright install
```

## Project Structure

- `notebooks/` - Main course content organized in 4 sections:
  - `01-python-fundamentals/` - Core Python concepts
  - `02-ai-apis/` - Working with AI services
  - `03-automation-projects/` - Real-world automation projects
  - `04-exercises/` - Practice problems and solutions
- `scripts/` - Standalone Python automation scripts and utilities
- `assets/` - Supporting files, sample data, and resources
- `main.py` - Basic entry point (minimal functionality)

## Key Dependencies

- **AI Libraries**: `openai`, `anthropic`, `ollama`
- **Data Science**: `pandas`, `matplotlib`, `numpy`
- **Web Scraping**: `requests`, `beautifulsoup4`, `playwright`
- **Jupyter**: `jupyterlab`, `ipykernel`, `ipywidgets`

## Architecture Notes

### AI Tools Module
The `scripts/ai_tools.py` module provides a unified interface for interacting with different AI providers:
- `ask_ai()` - Works with OpenAI (default) and Anthropic models
- `ask_local_ai()` - Works with local Ollama models
- Automatically handles API client initialization

### Demo Utilities
The `scripts/demo_utils.py` provides Jupyter notebook display utilities:
- `display_chat_message()` - Formats chat messages for notebook display
- `display_comparison()` - Shows side-by-side AI responses

### Environment Configuration
- Copy `.env.example` to `.env` and add API keys:
  ```
  OPENAI_API_KEY=<your openai api key>
  ANTHROPIC_API_KEY=<your claude api key>
  ```

## Working with Notebooks

- Notebooks are self-contained but build on previous concepts
- Run notebooks in numerical order within each section
- The custom kernel `oreilly-automate-py` should be used for consistent environment
- Sample data and resources are in the `assets/` folder

## Testing and Quality

This is an educational project without formal testing infrastructure. When making changes:
- Test scripts individually using `uv run python scripts/<script_name>.py`
- Verify notebooks run end-to-end in Jupyter Lab
- Ensure API keys are properly configured for AI-related functionality