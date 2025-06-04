#!/bin/bash

# Set project name (adjust as needed)
PROJECT_NAME="my-uv-project"
KERNEL_NAME="My UV Project"

# Exit if any command fails
set -e

echo "🔧 Initializing project..."
uv init --bare

echo "📦 Installing JupyterLab and ipykernel..."
uv add --dev jupyterlab ipykernel pandas matplotlib numpy openai anthropic

echo "🧠 Registering Jupyter kernel..."
uv run python -m ipykernel install --user --name="$PROJECT_NAME" --display-name "$KERNEL_NAME"

echo "✅ Setup complete. Run with:"
echo "uv run jupyter lab"
