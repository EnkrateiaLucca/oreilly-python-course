#!/bin/bash
set -e

echo "Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

echo "Installing Python dependencies with uv..."
uv sync

echo "Installing Jupyter kernel..."
uv run ipython kernel install --user --env VIRTUAL_ENV "$(pwd)/.venv" --name=oreilly-automate-py

echo "Installing Playwright browsers..."
uv run playwright install --with-deps chromium

echo ""
echo "============================================"
echo "  Setup complete!"
echo "============================================"
echo ""
echo "  Next steps:"
echo "  1. Create a .env file with your API keys:"
echo "     cp .env.example .env"
echo "     Then edit .env and add your keys."
echo ""
echo "  2. Launch Jupyter Lab:"
echo "     uv run --with jupyter jupyter lab"
echo ""
echo "============================================"
