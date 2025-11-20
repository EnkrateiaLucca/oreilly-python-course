# /// script
# requires-python = ">=3.12"
# dependencies = ["prompt_toolkit", "anthropic", "openai"]
# ///
"""
Vibescriptor - An AI-powered automation assistant for Python beginners.

This tool helps students learn to create Python automation scripts by:
1. Analyzing their automation requests
2. Determining feasibility with simple Python scripts
3. Generating executable scripts with UV inline metadata
4. Providing guidance when automation isn't straightforward
"""

import os
import sys
import json
import platform
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass

from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document


@dataclass
class Message:
    """Represents a single message in the conversation."""
    role: str
    content: str | List[Dict[str, Any]]


class AIBackend:
    """Handles communication with AI providers (OpenAI or Claude)."""

    def __init__(self, provider: str = "auto"):
        """
        Initialize the AI backend.

        Args:
            provider: 'openai', 'claude', or 'auto' (auto-detect based on env vars)
        """
        self.provider = provider
        self.client = None
        self.conversation_history: List[Dict[str, Any]] = []

        # System prompt that defines the agent's behavior
        self.system_prompt = """You are Vibescriptor, an AI automation assistant helping students learn Python automation.

Your role is to:
1. Analyze automation requests and determine if they can be solved with a simple Python script
2. If feasible: Generate a complete, runnable Python script with UV inline metadata
3. If not feasible: Explain why and guide the student to rethink their approach
4. Use tools when needed: read/write files, execute commands (with approval), or search the web

CRITICAL - When generating Python scripts, you MUST:
- ALWAYS start with UV inline metadata in this exact format:
  # /// script
  # requires-python = ">=3.10"
  # dependencies = [
  #   "requests>=2.31.0",
  #   "beautifulsoup4",
  # ]
  # ///
- Include ALL required dependencies with version constraints
- Make scripts immediately runnable with: uv run script_name.py
- NO setup.py, NO requirements.txt, NO pip install - ONLY UV inline metadata
- Add a clear docstring explaining what the script does and how to run it
- Include helpful comments for learning purposes
- Follow Python best practices (type hints, error handling, clear variable names)
- Structure code with functions, not just top-level statements
- Add a main() function and if __name__ == "__main__": guard

Script Template (ALWAYS follow this pattern):
```python
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "package-name>=version",
# ]
# ///

\"\"\"
Brief description of what this script does.

Usage: uv run script_name.py
\"\"\"

import sys
from pathlib import Path

def main():
    \"\"\"Main function.\"\"\"
    # Implementation here
    pass

if __name__ == "__main__":
    main()
```

When something isn't feasible:
- Explain the specific challenges (API limitations, complex UI interactions, etc.)
- Suggest simpler alternatives or breaking the problem into steps
- Help students understand what automation can and cannot do easily
- Guide them to rethink the problem in a way that IS automatable

You have access to these tools:
- read_file: Read contents of a file (students can reference files with @filename)
- write_file: Create or update files (ALWAYS use this for generated scripts)
- execute_command: Run bash/PowerShell commands (requires approval)
- web_search: Search for information online

Be encouraging, educational, and help students build automation skills progressively.
Remember: EVERY Python script you generate must be ready to run with 'uv run script.py' - no exceptions!"""

        self._initialize_client()

    def _initialize_client(self):
        """Initialize the appropriate AI client based on available API keys."""
        if self.provider == "auto":
            # Auto-detect based on environment variables
            if os.getenv("OPENAI_API_KEY"):
                self.provider = "openai"
            elif os.getenv("ANTHROPIC_API_KEY"):
                self.provider = "claude"
            else:
                raise ValueError(
                    "No API keys found! Please set either OPENAI_API_KEY or ANTHROPIC_API_KEY "
                    "environment variable."
                )

        if self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI()
            self.model = "gpt-4o"
        elif self.provider == "claude":
            import anthropic
            self.client = anthropic.Anthropic()
            self.model = "claude-3-5-sonnet-20241022"
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return tool definitions in the format expected by the AI provider."""
        tools = [
            {
                "name": "read_file",
                "description": "Read the contents of a file. Use when the user references a file with @ or when you need to see file contents.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path to the file to read (can be absolute or relative)"
                        }
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "write_file",
                "description": "Write content to a file. Use this to create Python automation scripts or save other content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path where the file should be written"
                        },
                        "content": {
                            "type": "string",
                            "description": "The content to write to the file"
                        }
                    },
                    "required": ["file_path", "content"]
                }
            },
            {
                "name": "execute_command",
                "description": "Execute a bash command (Linux/Mac) or PowerShell command (Windows). Requires user approval. Use for testing scripts or system operations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The command to execute"
                        },
                        "explanation": {
                            "type": "string",
                            "description": "A brief explanation of what this command does and why it's needed"
                        }
                    },
                    "required": ["command", "explanation"]
                }
            }
        ]

        # Add web search tool based on provider
        if self.provider == "openai":
            # OpenAI has built-in web search
            tools.append({
                "name": "web_search",
                "description": "Search the web for current information. Use when you need up-to-date information about libraries, APIs, or techniques.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        }
                    },
                    "required": ["query"]
                }
            })

        return tools

    def send_message(self, user_message: str) -> tuple[str, List[Dict[str, Any]]]:
        """
        Send a message to the AI and get a response.

        Returns:
            Tuple of (response_text, tool_calls)
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        if self.provider == "openai":
            return self._send_openai_message()
        else:
            return self._send_claude_message()

    def _send_openai_message(self) -> tuple[str, List[Dict[str, Any]]]:
        """Send message using OpenAI API."""
        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + self.conversation_history

        tools = self._get_tool_definitions()

        # Convert tool format for OpenAI
        openai_tools = []
        for tool in tools:
            if tool["name"] != "web_search":  # Skip web_search as it's not a custom function
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": tool["parameters"]
                    }
                })

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=openai_tools if openai_tools else None
        )

        message = response.choices[0].message

        # Extract tool calls if any
        tool_calls = []
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_calls.append({
                    "id": tool_call.id,
                    "name": tool_call.function.name,
                    "arguments": json.loads(tool_call.function.arguments)
                })

        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": message.tool_calls
        })

        return message.content or "", tool_calls

    def _send_claude_message(self) -> tuple[str, List[Dict[str, Any]]]:
        """Send message using Claude API."""
        tools = self._get_tool_definitions()

        # Convert tools to Claude format
        claude_tools = []
        for tool in tools:
            if tool["name"] != "web_search":  # Claude handles web search differently
                claude_tools.append({
                    "name": tool["name"],
                    "description": tool["description"],
                    "input_schema": tool["parameters"]
                })

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=self.system_prompt,
            messages=self.conversation_history,
            tools=claude_tools if claude_tools else None
        )

        # Extract text and tool calls
        text_content = ""
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                text_content += block.text
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "name": block.name,
                    "arguments": block.input
                })

        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response.content
        })

        return text_content, tool_calls

    def add_tool_result(self, tool_call_id: str, tool_name: str, result: str):
        """Add a tool execution result to the conversation history."""
        if self.provider == "openai":
            self.conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": tool_name,
                "content": result
            })
        else:  # claude
            self.conversation_history.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_call_id,
                        "content": result
                    }
                ]
            })


class ToolExecutor:
    """Handles execution of tools requested by the AI."""

    def __init__(self, working_directory: Path):
        self.working_directory = working_directory
        self.is_windows = platform.system() == "Windows"

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool and return the result."""
        if tool_name == "read_file":
            return self._read_file(arguments["file_path"])
        elif tool_name == "write_file":
            return self._write_file(arguments["file_path"], arguments["content"])
        elif tool_name == "execute_command":
            return self._execute_command(arguments["command"], arguments.get("explanation", ""))
        elif tool_name == "web_search":
            return self._web_search(arguments["query"])
        else:
            return f"Error: Unknown tool '{tool_name}'"

    def _read_file(self, file_path: str) -> str:
        """Read and return file contents."""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.working_directory / path

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            return f"Successfully read file '{file_path}':\n\n{content}"
        except Exception as e:
            return f"Error reading file '{file_path}': {str(e)}"

    def _write_file(self, file_path: str, content: str) -> str:
        """Write content to a file."""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.working_directory / path

            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            return f"Successfully wrote to file '{file_path}'"
        except Exception as e:
            return f"Error writing file '{file_path}': {str(e)}"

    def _execute_command(self, command: str, explanation: str) -> str:
        """Execute a shell command with user approval."""
        # Display command and ask for approval
        print(f"\n{'='*60}")
        print("🔧 Command Execution Request")
        print(f"{'='*60}")
        print(f"Command: {command}")
        print(f"Purpose: {explanation}")
        print(f"{'='*60}")

        approval = input("Execute this command? (yes/no): ").strip().lower()

        if approval not in ['yes', 'y']:
            return "Command execution declined by user."

        try:
            # Execute command
            if self.is_windows:
                result = subprocess.run(
                    ["powershell", "-Command", command],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.working_directory
                )
            else:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.working_directory
                )

            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"

            return f"Command executed successfully:\n{output}"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 30 seconds"
        except Exception as e:
            return f"Error executing command: {str(e)}"

    def _web_search(self, query: str) -> str:
        """Placeholder for web search - in practice, this would use a search API."""
        return f"Web search for '{query}' - This feature requires additional API setup."


class FilePathCompleter(Completer):
    """Custom completer for file paths after @ symbol."""

    def __init__(self, working_directory: Path):
        """
        Initialize the file path completer.

        Args:
            working_directory: The base directory to search for files
        """
        self.working_directory = working_directory

    def get_completions(self, document: Document, complete_event):
        """
        Generate file path completions.

        This method is called by prompt_toolkit to get completion suggestions.
        It only activates when the user types '@' followed by characters.
        """
        text = document.text_before_cursor

        # Find the last @ symbol
        last_at = text.rfind('@')

        # Only provide completions if @ is present
        if last_at == -1:
            return

        # Get the partial path after @
        partial_path = text[last_at + 1:]

        # Determine search directory and pattern
        if '/' in partial_path or '\\' in partial_path:
            # User is typing a path with directories
            path_obj = Path(partial_path)
            if path_obj.is_absolute():
                search_dir = path_obj.parent
                prefix = path_obj.name
            else:
                search_dir = self.working_directory / path_obj.parent
                prefix = path_obj.name
        else:
            # Just a filename, search in working directory
            search_dir = self.working_directory
            prefix = partial_path

        # Ensure search directory exists
        if not search_dir.exists():
            return

        # Find matching files and directories
        try:
            for item in sorted(search_dir.iterdir()):
                # Skip hidden files and special directories
                if item.name.startswith('.'):
                    continue

                # Check if item matches the prefix
                if item.name.lower().startswith(prefix.lower()):
                    # Calculate relative path from working directory
                    try:
                        relative_path = item.relative_to(self.working_directory)
                        display_path = str(relative_path)
                    except ValueError:
                        # If item is not relative to working_directory, use absolute
                        display_path = str(item)

                    # Add / for directories
                    if item.is_dir():
                        display_path += '/'

                    # Calculate how much of the current input to replace
                    # We want to replace everything after the @
                    start_position = -len(partial_path)

                    yield Completion(
                        text=display_path,
                        start_position=start_position,
                        display=f"@{display_path}",
                        display_meta="📁 directory" if item.is_dir() else "📄 file"
                    )
        except PermissionError:
            # Silently skip directories we can't read
            pass


class ChatInterface:
    """Manages the interactive chat interface using prompt_toolkit."""

    def __init__(self, working_directory: Path):
        """
        Initialize the chat interface.

        Args:
            working_directory: The base directory for file operations
        """
        self.working_directory = working_directory
        self.style = Style.from_dict({
            'prompt': '#00aa00 bold',
            'assistant': '#00aaff',
            'system': '#ffaa00',
            'error': '#ff0000 bold',
        })

        # Create history file in the vibescriptor directory
        history_file = Path(__file__).parent / ".vibescriptor_history"

        # Create file path completer
        file_completer = FilePathCompleter(working_directory)

        self.session = PromptSession(
            history=FileHistory(str(history_file)),
            auto_suggest=AutoSuggestFromHistory(),
            completer=file_completer,
            complete_while_typing=True,
        )

    def print_welcome(self):
        """Print welcome message."""
        print("\n" + "="*60)
        print("🤖 Welcome to Vibescriptor!")
        print("="*60)
        print("Your AI-powered Python automation assistant")
        print("\nI can help you:")
        print("  • Determine if your automation idea is feasible")
        print("  • Generate ready-to-run Python scripts (uv run script.py)")
        print("  • Guide you when automation gets complex")
        print("\nSpecial features:")
        print("  • Type @ to autocomplete file paths (try it!)")
        print("  • Use @filename to reference files in your messages")
        print("  • All generated scripts include UV inline metadata")
        print("\nCommands:")
        print("  • 'exit' or 'quit' - Leave the application")
        print("  • 'clear' - Start a new conversation")
        print("="*60 + "\n")

    def get_user_input(self) -> Optional[str]:
        """Get input from user with nice prompt."""
        try:
            message = self.session.prompt(
                HTML('<prompt>You: </prompt>'),
                style=self.style
            )
            return message.strip()
        except (EOFError, KeyboardInterrupt):
            return None

    def print_assistant_message(self, message: str):
        """Print assistant's message."""
        if message:
            print(f"\n🤖 Vibescriptor: {message}\n")

    def print_system_message(self, message: str):
        """Print system message."""
        print(f"\n💡 {message}\n")

    def print_error(self, message: str):
        """Print error message."""
        print(f"\n❌ Error: {message}\n")


def extract_file_references(message: str) -> tuple[str, List[str]]:
    """
    Extract @file references from message.

    Returns:
        Tuple of (cleaned_message, list_of_file_paths)
    """
    import re

    # Find all @filename patterns
    pattern = r'@([^\s]+)'
    files = re.findall(pattern, message)

    return message, files


def main():
    """Main application loop."""
    # Get working directory
    working_dir = Path.cwd()

    # Initialize components
    interface = ChatInterface(working_dir)
    interface.print_welcome()

    # Initialize AI backend
    try:
        backend = AIBackend(provider="auto")
        interface.print_system_message(f"Using {backend.provider.upper()} as AI provider")
    except ValueError as e:
        interface.print_error(str(e))
        return 1

    # Initialize tool executor
    tool_executor = ToolExecutor(working_dir)

    # Main conversation loop
    while True:
        # Get user input
        user_input = interface.get_user_input()

        if user_input is None:
            print("\nGoodbye! Happy automating! 🚀")
            break

        if not user_input:
            continue

        # Handle special commands
        if user_input.lower() in ['exit', 'quit']:
            print("\nGoodbye! Happy automating! 🚀")
            break

        if user_input.lower() == 'clear':
            backend.conversation_history = []
            interface.print_system_message("Conversation cleared. Starting fresh!")
            continue

        # Extract file references
        message, file_refs = extract_file_references(user_input)

        # If files are referenced, read them and add context
        if file_refs:
            file_context = "\n\nReferenced files:\n"
            for file_path in file_refs:
                result = tool_executor.execute_tool("read_file", {"file_path": file_path})
                file_context += f"\n{result}\n"
            message += file_context

        try:
            # Send message to AI
            response_text, tool_calls = backend.send_message(message)

            # Display initial response if any
            if response_text:
                interface.print_assistant_message(response_text)

            # Execute any tool calls
            while tool_calls:
                for tool_call in tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["arguments"]
                    tool_id = tool_call["id"]

                    # Show what tool is being used
                    interface.print_system_message(
                        f"Using tool: {tool_name} with args: {json.dumps(tool_args, indent=2)}"
                    )

                    # Execute tool
                    result = tool_executor.execute_tool(tool_name, tool_args)

                    # Add result to conversation
                    backend.add_tool_result(tool_id, tool_name, result)

                # Get follow-up response from AI after tool execution
                response_text, tool_calls = backend.send_message("")

                if response_text:
                    interface.print_assistant_message(response_text)

        except Exception as e:
            interface.print_error(f"An error occurred: {str(e)}")
            import traceback
            traceback.print_exc()

    return 0


if __name__ == "__main__":
    sys.exit(main())
