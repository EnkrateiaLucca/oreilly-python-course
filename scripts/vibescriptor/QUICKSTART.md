# Vibescriptor Quick Start Guide

Get up and running with Vibescriptor in 5 minutes!

## Step 1: Set Your API Key

Choose one:

### Option A: OpenAI (Recommended)
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### Option B: Claude (Alternative)
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

**Tip**: Add this to your `~/.zshrc` or `~/.bashrc` to make it permanent.

## Step 2: Run Vibescriptor

From the project root:
```bash
cd scripts/vibescriptor
uv run python vibescriptor.py
```

## Step 3: Try Your First Automation

Here are some great starter prompts:

### Easy Wins 🎯

```
I want to rename all .txt files in a folder to include today's date
```

```
Create a script that backs up a folder by copying it with a timestamp
```

```
I need to download all images from a list of URLs
```

### Learning Opportunities 📚

```
I want to automate my email responses
```
*(This will help you understand the limits of simple automation)*

```
Can I scrape product prices from Amazon?
```
*(This will teach you about challenges with web scraping)*

### With File References 📁

```
I have a CSV file @data.csv with sales data. Can you create a summary report?
```

## Step 4: Run Your Generated Script

When Vibescriptor creates a script for you:

1. It saves it to the current directory
2. Run it with: `uv run script_name.py`
3. The script includes all dependencies automatically!

## Common Patterns

### Pattern 1: File Organization
```
You: I want to organize my downloads by file type
Bot: [Creates organize_downloads.py]
You: uv run organize_downloads.py
```

### Pattern 2: Data Processing
```
You: Read @sales.csv and calculate monthly totals
Bot: [Reads file, creates analysis script]
```

### Pattern 3: Web Automation
```
You: Download the top 10 posts from a subreddit
Bot: [Creates web scraping script with proper error handling]
```

## Tips for Success

1. **Be Specific**: Instead of "organize files", say "organize files by extension into folders"

2. **Start Simple**: Begin with file operations before trying complex web automation

3. **Use @ References**: When working with existing files, use `@filename` to give context

4. **Iterate**: If the first solution isn't perfect, ask for modifications

5. **Learn from Rejections**: When Vibescriptor says something isn't feasible, it's teaching you important lessons

## Understanding Feasibility

### ✅ Usually Feasible
- File operations (rename, move, organize)
- Data processing (CSV, JSON, text files)
- API interactions (if public API available)
- Web scraping (simple sites)
- PDF generation/manipulation
- Image processing (resize, convert, organize)

### ⚠️ Sometimes Feasible
- Web scraping (complex sites with JavaScript)
- Browser automation (needs Playwright/Selenium)
- Email automation (needs proper authentication)
- Database operations (needs database setup)

### ❌ Usually Not Feasible (for simple scripts)
- GUI automation of desktop apps
- Video game automation
- Real-time system monitoring with complex logic
- Anything requiring computer vision
- Complex authentication flows

## Troubleshooting Quick Fixes

### "No API keys found"
```bash
# Make sure you exported the key
echo $OPENAI_API_KEY
# Should print your key
```

### "Module not found"
```bash
# From project root
uv sync
```

### "Permission denied" on scripts
```bash
chmod +x your_script.py
```

## Next Steps

After getting comfortable:

1. **Modify generated scripts** - Add your own features
2. **Combine scripts** - Chain multiple automations together
3. **Share your automations** - Help other students learn
4. **Push boundaries** - Try increasingly complex requests to learn the limits

## Example Session

Here's what a typical session looks like:

```
🤖 Welcome to Vibescriptor!
Your AI-powered Python automation assistant
==========================================================

You: I want to create a script that counts lines of code in my Python project

🤖 Vibescriptor: Great idea! I'll create a script that:
1. Walks through your project directory
2. Finds all .py files
3. Counts lines (total, code, comments, blank)
4. Displays a summary

💡 Using tool: write_file with args: {
  "file_path": "count_lines.py",
  "content": "# /// script\n..."
}

🤖 Vibescriptor: I've created count_lines.py for you! Run it with:
uv run count_lines.py

The script will analyze the current directory and show you statistics
about your Python code. It skips virtual environments and cache folders.

You: exit

Goodbye! Happy automating! 🚀
```

## Have Fun! 🎉

Remember: The goal is to learn. Every interaction teaches you something about:
- What automation can do
- How to break down problems
- Python best practices
- When to use automation vs. manual work

Happy automating!
