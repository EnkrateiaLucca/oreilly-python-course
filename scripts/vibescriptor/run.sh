#!/bin/bash
# Launcher script for Vibescriptor

# Check if API key is set
if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: No API key found!"
    echo ""
    echo "Please set one of these environment variables:"
    echo "  export OPENAI_API_KEY='your-key'"
    echo "  export ANTHROPIC_API_KEY='your-key'"
    echo ""
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Navigate to project root (two levels up from scripts/vibescriptor)
PROJECT_ROOT="$SCRIPT_DIR/../.."

# Run vibescriptor
cd "$PROJECT_ROOT" && uv run python scripts/vibescriptor/vibescriptor.py
