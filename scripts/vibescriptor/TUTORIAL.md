# Vibescriptor Tutorial: Learning Through Examples

This tutorial walks you through increasingly complex automation scenarios to help you master Python automation with Vibescriptor.

## Level 1: File Operations (Beginner)

### Exercise 1.1: Simple File Renaming

**Your Task**: Rename all `.txt` files in a folder to include today's date.

**What to ask Vibescriptor**:
```
I want to rename all .txt files in the current folder to include today's date at the beginning of the filename
```

**What you'll learn**:
- File system operations with `pathlib`
- Working with dates in Python
- Iterating over files
- String formatting

**Expected output**: A script that transforms `notes.txt` → `2024-01-20_notes.txt`

---

### Exercise 1.2: File Organization

**Your Task**: Organize files by type into folders.

**What to ask Vibescriptor**:
```
Create a script that organizes files in a folder by their extension. Move images to Images/, documents to Documents/, etc.
```

**What you'll learn**:
- File extension detection
- Directory creation
- File moving operations
- Exception handling

---

## Level 2: Data Processing (Intermediate)

### Exercise 2.1: CSV Analysis

**Your Task**: Analyze the sample data.

**What to ask Vibescriptor**:
```
I want to analyze @sample_data.csv and create a summary showing:
- Average age
- Average score
- Count by city
- Top 3 scores
```

**What you'll learn**:
- Reading CSV files
- Data aggregation
- Working with pandas (or pure Python)
- Formatted output

---

### Exercise 2.2: Data Transformation

**Your Task**: Convert between data formats.

**What to ask Vibescriptor**:
```
Create a script that converts @sample_data.csv to JSON format, grouping records by city
```

**What you'll learn**:
- CSV to JSON conversion
- Data grouping and transformation
- JSON formatting
- File I/O operations

---

## Level 3: Web Operations (Intermediate-Advanced)

### Exercise 3.1: Simple Web Scraping

**Your Task**: Extract data from a website.

**What to ask Vibescriptor**:
```
I want to scrape the top 10 posts from a website. Can you help me understand if this is feasible and how to approach it?
```

**What you'll learn**:
- When web scraping is appropriate
- Using requests and BeautifulSoup
- Handling HTML parsing
- Rate limiting and politeness

**Note**: Vibescriptor will ask for the specific website and help you understand if it's scrapeable.

---

### Exercise 3.2: API Interaction

**Your Task**: Work with a public API.

**What to ask Vibescriptor**:
```
Create a script that fetches weather data from a public API for a given city
```

**What you'll learn**:
- HTTP requests
- Working with JSON APIs
- Error handling for network operations
- API best practices

---

## Level 4: Automation Chains (Advanced)

### Exercise 4.1: Multi-Step Workflow

**Your Task**: Create a backup and cleanup workflow.

**What to ask Vibescriptor**:
```
I want a script that:
1. Creates a backup of a folder (with timestamp)
2. Removes files older than 30 days from the original
3. Logs what was done
```

**What you'll learn**:
- Multi-step workflows
- Date comparisons
- Logging
- Backup strategies

---

### Exercise 4.2: Scheduled Automation

**Your Task**: Learn about scheduling.

**What to ask Vibescriptor**:
```
How can I make a script that checks a folder for new files every hour and processes them?
```

**What you'll learn**:
- Scheduling concepts (cron, Task Scheduler)
- Long-running scripts
- File watching
- Process management

---

## Level 5: Understanding Limitations (Important!)

### Exercise 5.1: Learning from "No"

**Your Task**: Try something complex.

**What to ask Vibescriptor**:
```
I want to automate clicking buttons in a desktop application
```

**What you'll learn**:
- Why GUI automation is challenging
- Alternative approaches
- When to use Playwright vs simpler tools
- How to break down complex problems

---

### Exercise 5.2: Security and Ethics

**Your Task**: Understand boundaries.

**What to ask Vibescriptor**:
```
Can I create a script that logs into my social media accounts and posts automatically?
```

**What you'll learn**:
- Authentication challenges
- API vs web scraping
- Terms of Service considerations
- Security best practices

---

## Practice Projects

Once you're comfortable, try these complete projects:

### Project 1: Photo Organizer
Create a script that organizes photos by date taken (from EXIF data) into year/month folders.

**Hint**: Ask about EXIF data first, then build iteratively.

---

### Project 2: Download Manager
Build a robust file downloader that:
- Accepts a list of URLs from a file
- Downloads with progress bars
- Handles errors and retries
- Logs successes and failures

---

### Project 3: Report Generator
Create a script that:
- Reads data from CSV
- Generates statistics
- Creates a PDF report with charts
- Emails the report (advanced)

---

## Tips for Each Level

### Level 1 Tips:
- Start with very specific descriptions
- Ask for error handling
- Request comments in the code
- Try running the scripts on test data first

### Level 2 Tips:
- Always work with sample data first
- Ask Vibescriptor to explain the approach before coding
- Request validation of input data
- Consider edge cases

### Level 3 Tips:
- Check website terms of service
- Start with simple public APIs
- Ask about rate limiting
- Understand when authentication is needed

### Level 4 Tips:
- Break complex tasks into steps
- Test each step independently
- Ask about different approaches
- Consider error recovery

### Level 5 Tips:
- Accept when things are too complex
- Learn from the explanations
- Ask for alternatives
- Understand the "why" behind limitations

---

## Interactive Learning Pattern

Follow this pattern for best results:

1. **Ask**: Describe what you want to automate
2. **Understand**: Read Vibescriptor's feasibility analysis
3. **Review**: Examine the generated code
4. **Test**: Run the script on sample data
5. **Iterate**: Ask for modifications or improvements
6. **Learn**: Understand why it works this way

### Example Iteration:

```
You: Create a file organizer

Bot: [Creates basic organizer]

You: Can you add a dry-run mode that shows what would be moved without moving it?

Bot: [Adds --dry-run flag]

You: And add logging to a file?

Bot: [Adds logging functionality]
```

---

## Common Mistakes and How to Fix Them

### Mistake 1: Too Vague
❌ "Help me with files"
✅ "Rename all JPG files in my Downloads folder to include the date taken"

### Mistake 2: Too Complex at Once
❌ "Create a complete photo management system with AI tagging, cloud backup, and mobile app"
✅ Start with: "Organize photos by date into folders"

### Mistake 3: Not Using File References
❌ "Process my CSV file" (without sharing it)
✅ "Process @my_data.csv and calculate averages"

### Mistake 4: Not Testing Incrementally
❌ Running a file deletion script on important data immediately
✅ Test on a copy first, add --dry-run modes

### Mistake 5: Ignoring Limitations
❌ Insisting on automating something that requires human judgment
✅ Understanding when automation isn't appropriate

---

## Advanced Techniques

### Technique 1: Iterative Development
Build complex scripts step by step:
1. First: Basic functionality
2. Second: Error handling
3. Third: Progress reporting
4. Fourth: Configuration options
5. Fifth: Logging and debugging

### Technique 2: Using @ References Effectively
```
You: Compare @old_version.py with @new_version.py and explain the differences
```

### Technique 3: Learning from Generated Code
After getting a script:
- Read every line and understand it
- Look up unfamiliar functions
- Modify it slightly to see what changes
- Ask Vibescriptor to explain specific parts

### Technique 4: Building a Toolkit
Save good scripts and build a personal automation toolkit:
- File operations (rename, organize, backup)
- Data processing (CSV, JSON, Excel)
- Web operations (download, scrape, API)
- Report generation (PDF, charts, summaries)

---

## Troubleshooting Your Learning

### "I don't understand the generated code"
**Solution**: Ask Vibescriptor to explain specific parts:
```
Can you explain what the 'pathlib.Path.glob()' method does in the script you just created?
```

### "The script doesn't work"
**Solution**: Share the error message:
```
I got this error when running the script: [paste error]
Can you help me fix it?
```

### "I want to modify the script but don't know how"
**Solution**: Describe the change:
```
The script you created saves to CSV. How can I modify it to save to JSON instead?
```

### "I'm not sure if my idea is feasible"
**Solution**: Just ask! That's what Vibescriptor is for:
```
Is it possible to automate [your idea]? What are the challenges?
```

---

## Assessment: Are You Ready?

You're mastering automation when you can:

✅ Describe automation tasks clearly and specifically
✅ Understand when automation is feasible vs. too complex
✅ Read and modify generated Python scripts
✅ Debug simple errors in automation scripts
✅ Break complex tasks into smaller, automatable steps
✅ Consider error handling and edge cases
✅ Understand the security and ethical implications

---

## Next Steps

After completing this tutorial:

1. **Build Your Own Projects**: Identify real automation needs in your workflow
2. **Share Your Scripts**: Help other students by sharing useful automations
3. **Contribute**: Suggest improvements to Vibescriptor itself
4. **Go Deeper**: Learn more about libraries used in generated scripts
5. **Teach Others**: The best way to learn is to teach

---

## Resources for Continued Learning

- **Python Documentation**: https://docs.python.org/3/
- **UV Documentation**: https://docs.astral.sh/uv/
- **Requests Library**: https://requests.readthedocs.io/
- **Pathlib Guide**: https://docs.python.org/3/library/pathlib.html
- **BeautifulSoup**: https://www.crummy.com/software/BeautifulSoup/
- **Pandas**: https://pandas.pydata.org/

Remember: Every expert was once a beginner. Take it step by step, and don't be afraid to ask "dumb" questions. That's what Vibescriptor is here for!

Happy automating! 🚀
