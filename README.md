# O'Reilly Live Trainining - Automate Tasks with Python + AI 

## Recommended Setup

### 1. Install UV:

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Setup Environment

**Linux/macOS:**
```bash
#!/bin/bash

# Set project name (adjust as needed)
PROJECT_NAME="oreilly-vibe-scripting"
KERNEL_NAME="oreilly-vibe-scripting"

# Exit if any command fails
set -e

echo "🔧 Initializing project..."
uv init --bare

echo "📦 Installing JupyterLab and ipykernel..."
uv add --dev jupyterlab ipykernel
uv add openai pandas anthropic ollama requests beautifulsoup4 matplotlib ipywidgets playwright

echo "🧠 Registering Jupyter kernel..."
uv run python -m ipykernel install --user --name="$PROJECT_NAME" --display-name "$KERNEL_NAME"

echo "✅ Setup complete. Run with:"
echo "uv run jupyter lab"
```

**Windows (PowerShell):**

```powershell
# Set project name (adjust as needed)
$projectName = "my-uv-project"
$kernelDisplayName = "My UV Project"
Write-Output "🔧 Initializing project..."
uv init --bare
Write-Output "📦 Installing JupyterLab and ipykernel..."
uv add --dev jupyterlab ipykernel
Write-Output "🧠 Registering Jupyter kernel..."
uv run python -m ipykernel install --user --name=$projectName --display-name "$kernelDisplayName"
Write-Output "✅ Setup complete. Run with:"
Write-Output "uv run jupyter lab"
```

### 3. Setup your API keys:

1. Openai [API key](https://platform.openai.com/)
2. Anthropic [API key](https://docs.anthropic.com/en/docs/get-started)

### Setup your .env file

- Change the `.env.example` file to `.env` and add your OpenAI API key.

```bash
OPENAI_API_KEY=<your openai api key>
ANTHROPIC_API_KEY=<your claude api key>
....
```

<!-- 1. [](notebooks/9.0-building-email-assistant.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly-python-course/blob/main/notebooks/9.0-building-email-assistant.ipynb) -->