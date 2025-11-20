# Vibescriptor 🤖

An AI-powered automation assistant that helps students learn Python automation by determining feasibility and generating executable scripts.

## What is Vibescriptor?

Vibescriptor is an interactive CLI tool that acts as a learning companion for Python automation. It helps students by:

1. **Analyzing automation requests** - Understanding what the student wants to automate
2. **Determining feasibility** - Deciding if it can be done with a simple Python script
3. **Generating scripts** - Creating complete, runnable scripts with UV inline metadata
4. **Providing guidance** - Explaining why something might not be feasible and suggesting alternatives

## Features

- 🤖 **Intelligent AI Backend** - Supports both OpenAI (GPT-4o) and Claude (Sonnet 3.5)
- 📁 **File Operations** - Read and write files with simple commands
- 💻 **Safe Command Execution** - Run bash/PowerShell commands with approval prompts
- 🎯 **Smart File References** - Type `@` to autocomplete file paths, then reference them in your conversation
- 📝 **UV Inline Metadata** - ALL generated scripts include dependency information for instant execution
- 🎨 **Beautiful CLI** - Built with prompt_toolkit with autocomplete, history, and suggestions
- ⚡ **Ready-to-Run Scripts** - Every generated script works immediately with `uv run script.py`

## Installation

This tool is part of the O'Reilly Python course repository. The dependencies are already installed via the project's `pyproject.toml`.

### Prerequisites

You need at least one of these API keys:
- OpenAI API key (preferred)
- Anthropic Claude API key (fallback)

### Setup

1. Set your API key as an environment variable:

```bash
# For OpenAI (recommended)
export OPENAI_API_KEY="your-openai-api-key"

# OR for Claude (if no OpenAI key available)
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

2. Navigate to the vibescriptor directory:

```bash
cd scripts/vibescriptor
```

3. Run the tool:

```bash
uv run python vibescriptor.py
```

Or from the project root:

```bash
uv run python scripts/vibescriptor/vibescriptor.py
```

## How to Use

### Basic Usage

Start the tool and describe what you want to automate:

```
You: I want to rename all my photos to include the date they were taken

🤖 Vibescriptor: That's definitely possible! I can create a Python script that...
```

### Referencing Files with Autocomplete

Vibescriptor includes smart file path autocomplete! Just type `@` and start typing:

```
You: Can you help me analyze @da<TAB>
     [Autocomplete shows: @data.csv, @dashboard.py, etc.]
You: Can you help me analyze @data.csv and create a summary?

🤖 Vibescriptor: Let me read that file first...
```

**Autocomplete features:**
- Press `TAB` or `→` to complete suggestions
- Works with nested directories: `@scripts/my<TAB>`
- Shows file/directory icons for easy identification
- Case-insensitive matching
- Real-time file system scanning

### Special Commands

- `exit` or `quit` - Exit the application
- `clear` - Start a new conversation (clears history)
- `@filename` - Reference a file (with autocomplete support!)

## Example Interactions

### Example 1: Feasible Automation

```
You: I want a script that organizes my downloads folder by file type

🤖 Vibescriptor: Great idea! This is very feasible with Python. I'll create a script
that categorizes files by extension and moves them into organized folders.

[Creates organize_downloads.py with UV inline metadata]

You can run it with: uv run organize_downloads.py
```

### Example 2: Guidance on Complex Automation

```
You: I want to automate playing my favorite video game

🤖 Vibescriptor: That's a challenging automation for a simple Python script. Here's why:

1. Game automation often requires computer vision and precise timing
2. Many games have anti-cheat systems that block automation
3. It may violate the game's terms of service

Instead, consider:
- Automating game-related tasks (organizing screenshots, tracking stats)
- Creating tools to analyze game data
- Building a Discord bot for game community management

Would you like help with any of these alternatives?
```

### Example 3: Using File References

```
You: I have a list of URLs in @urls.txt. Can you create a script to download them all?

💡 Using tool: read_file with args: {"file_path": "urls.txt"}

🤖 Vibescriptor: I see you have 15 URLs in that file. I'll create a script that:
1. Reads the URLs from the file
2. Downloads each one with progress tracking
3. Handles errors gracefully

[Creates download_urls.py]
```

## How It Works

### AI Agent Architecture

Vibescriptor uses a **tool-calling architecture** where the AI can:

1. **Reason about tasks** - Determine if automation is feasible
2. **Use tools** - Read/write files, execute commands, search the web
3. **Generate code** - Create complete Python scripts with proper structure
4. **Iterate** - Refine solutions based on user feedback

### Tool System

The agent has access to these tools:

- **read_file**: Read file contents (triggered by @ references or agent decision)
- **write_file**: Create or update files (for generating scripts)
- **execute_command**: Run shell commands with user approval
- **web_search**: Search for current information (provider-dependent)

### Safety Features

- **Command approval**: All bash/PowerShell commands require explicit user approval
- **Sandboxed execution**: Commands run with timeout limits
- **Error handling**: Graceful failure with helpful error messages

## Generated Script Format

Scripts generated by Vibescriptor use UV inline metadata:

```python
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests",
#   "beautifulsoup4",
# ]
# ///

"""
Script description here
"""

# Your automation code here
```

Run with:
```bash
uv run script.py
```

## Educational Benefits

Vibescriptor helps students learn:

1. **Problem Decomposition** - Breaking complex tasks into automatable parts
2. **Feasibility Analysis** - Understanding what can and cannot be automated
3. **Tool Usage** - Working with files, APIs, and system commands
4. **Best Practices** - Generated scripts follow Python conventions
5. **Dependency Management** - Using modern tools like UV for script dependencies

## Troubleshooting

### "No API keys found" Error

Make sure you have set at least one API key:

```bash
export OPENAI_API_KEY="your-key"
# OR
export ANTHROPIC_API_KEY="your-key"
```

### Import Errors

Make sure you're in the correct Python environment:

```bash
# From project root
uv sync
uv run python scripts/vibescriptor/vibescriptor.py
```

### Command Execution Issues

On some systems, you may need to grant additional permissions for command execution. The tool will ask for approval before running any commands.

## Limitations

- Web search functionality requires additional API setup
- Command execution has a 30-second timeout
- Generated scripts are meant to be starting points and may need refinement
- Some complex automations may require manual implementation

## Contributing

This is an educational tool. Students are encouraged to:
- Experiment with different automation requests
- Modify the code to add new features
- Share interesting automation scripts they generate

## License

Part of the O'Reilly Live Training course materials.
