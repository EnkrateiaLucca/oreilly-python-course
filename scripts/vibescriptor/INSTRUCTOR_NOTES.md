# Vibescriptor - Instructor Notes

## Overview

Vibescriptor is a pedagogical tool designed to help students learn Python automation through guided AI assistance. It serves as a "training wheels" system that helps students understand:
1. What can be automated with Python
2. When automation is appropriate
3. How to structure automation scripts
4. Best practices in Python development

## Educational Philosophy

The tool is built on these principles:

### 1. Learning Through Boundaries
Students learn as much from understanding what *can't* be automated as what can. When Vibescriptor determines something isn't feasible, it provides educational explanations.

### 2. Progressive Complexity
Students can start with simple tasks (file renaming) and gradually work toward complex automations (multi-step workflows, API integrations).

### 3. Real-World Patterns
Generated scripts follow professional patterns:
- UV inline metadata for dependencies
- Proper error handling
- Clear documentation
- Type hints where appropriate

### 4. Safety First
Command execution requires approval, teaching students to be cautious about automated system operations.

## Architecture

### Core Components

```
vibescriptor.py
├── AIBackend (Handles OpenAI/Claude communication)
│   ├── Tool definitions
│   ├── Conversation management
│   └── Provider-specific implementations
├── ToolExecutor (Executes AI-requested tools)
│   ├── File operations (read/write)
│   ├── Command execution (with approval)
│   └── Web search (placeholder)
└── ChatInterface (User interaction)
    ├── Prompt toolkit integration
    ├── File reference extraction (@filename)
    └── Message formatting
```

### Design Decisions

**1. Dual Provider Support**
- OpenAI (primary): More widely available, good documentation
- Claude (fallback): Often more thoughtful for code generation
- Auto-detection based on environment variables

**2. Tool-Calling Architecture**
Both providers support native function/tool calling, allowing the AI to:
- Decide when to read files
- Choose when to execute commands
- Iteratively use tools to solve problems

**3. UV Inline Metadata**
Scripts include dependencies in /// script comments, making them:
- Self-contained
- Easy to run (`uv run script.py`)
- Portable across environments

**4. Safety Mechanisms**
- Command approval prompts
- 30-second timeout on commands
- Working directory scoped operations

## Teaching with Vibescriptor

### Recommended Classroom Flow

#### Week 1: Introduction
- Demonstrate basic file operations
- Show feasible vs. infeasible examples
- Have students try simple automations

#### Week 2: Data Processing
- CSV/JSON manipulation
- Data analysis scripts
- Introduce pandas through generated scripts

#### Week 3: Web Operations
- API interactions
- Simple web scraping
- Discuss ethics and ToS

#### Week 4: Complex Projects
- Multi-step workflows
- Error handling patterns
- Scheduling and deployment

### Common Student Challenges

**Challenge**: "It said my idea isn't feasible, but I saw it on YouTube"
**Response**: Great teaching moment! Discuss complexity, dependencies, and why "possible" doesn't mean "simple."

**Challenge**: "The generated script doesn't work"
**Response**: Perfect! Use this to teach debugging:
- Reading error messages
- Understanding stack traces
- Iterating with Vibescriptor to fix

**Challenge**: "I want to automate [something unethical]"
**Response**: Vibescriptor will guide them, but be ready to discuss:
- Terms of Service
- Legal considerations
- Ethical automation practices

### Assessment Ideas

**Assignment 1**: Personal Automation
- Student identifies a personal pain point
- Uses Vibescriptor to create solution
- Submits script + reflection on what they learned

**Assignment 2**: Teaching Others
- Student creates tutorial for specific automation
- Explains both the "how" and "when"
- Documents limitations encountered

**Assignment 3**: Complexity Analysis
- Given several automation ideas
- Analyze feasibility without running Vibescriptor
- Compare analysis with Vibescriptor's assessment

## Technical Details for Advanced Students

### Extending Vibescriptor

Students interested in tool development can:

**Add New Tools**:
```python
# In _get_tool_definitions()
{
    "name": "search_python_docs",
    "description": "Search Python documentation",
    "parameters": {...}
}

# In execute_tool()
def _search_python_docs(self, query):
    # Implementation
```

**Custom Providers**:
```python
# In AIBackend._initialize_client()
elif self.provider == "local":
    # Add Ollama or other local model
```

**Enhanced File References**:
Currently supports `@filename`, could extend to:
- `@dir/` (reference all files in directory)
- `@*.py` (reference by pattern)
- `@lines:10-20:file.py` (specific lines)

### Known Limitations

1. **Web Search**: Placeholder implementation - needs API setup
2. **Complex CLI**: No multi-line input, no command history search
3. **File References**: Simple regex, doesn't handle quoted paths
4. **Command Execution**: Limited to 30 seconds
5. **No Persistent State**: Each session is independent

## Troubleshooting for Instructors

### Students Can't Run It

**Check**:
```bash
# API key set?
echo $OPENAI_API_KEY

# In correct directory?
pwd

# Dependencies installed?
uv sync
```

### Generated Scripts Fail

**Common Causes**:
1. Missing dependencies (should be in /// script block)
2. Path issues (relative vs absolute)
3. Permissions problems
4. API limits hit

### Performance Issues

**If slow**:
- Check internet connection
- Verify API key quota
- Consider switching providers
- Look for rate limiting

## Future Enhancements

### Short Term
1. Better web search integration
2. Multi-line input support
3. Session save/load
4. Syntax highlighting in terminal

### Medium Term
1. Integration with VS Code
2. Script testing framework
3. Gallery of student-created scripts
4. Peer review features

### Long Term
1. Multi-agent collaboration
2. Visual workflow builder
3. Script optimization suggestions
4. Deployment assistance

## Discussion Prompts for Class

1. **Automation Ethics**: When is it appropriate to automate? When isn't it?

2. **AI-Assisted Development**: How does this change programming education?

3. **Dependency Management**: Why is UV inline metadata better than requirements.txt?

4. **Error Handling**: Why does good automation need more error handling than one-off scripts?

5. **Security**: What are the risks of executing AI-generated code?

## Additional Resources for Students

### Recommended Reading
- "Automate the Boring Stuff with Python" by Al Sweigart
- Python's pathlib documentation
- UV documentation on scripts
- "The Pragmatic Programmer" on automation

### Practice Datasets
Include in course materials:
- Sample CSV files (sales data, logs, etc.)
- JSON APIs for practice
- Image collections for organization tasks
- Text files for processing

### Related Tools
- **Playwright**: Browser automation
- **Pandas**: Data processing
- **Click**: CLI interfaces
- **Schedule**: Task scheduling

## Student Success Stories (Template)

Document and share:
- What they automated
- Challenges faced
- How they overcame them
- Time saved
- Skills learned

This creates a positive feedback loop and inspires other students.

## Assessment Rubric (Suggested)

**Script Functionality** (40%)
- Does it work as intended?
- Handles errors gracefully?
- Follows the specification?

**Code Quality** (30%)
- Clear variable names?
- Appropriate comments?
- Good structure?
- Proper error handling?

**Learning Reflection** (30%)
- Understands why it works?
- Can explain trade-offs?
- Identifies limitations?
- Suggests improvements?

## Final Notes

Vibescriptor is not meant to replace learning Python fundamentals. It's a **supplementary tool** that:
- Accelerates practical project work
- Provides real-world context
- Teaches professional patterns
- Makes automation approachable

The goal is to get students excited about automation while teaching them to think critically about when and how to apply it.

Students should graduate from Vibescriptor to writing their own automation tools, carrying forward the patterns and principles they learned.

---

## Contact and Contributions

This tool is part of the O'Reilly Live Training course materials. Instructors are encouraged to:
- Share success stories
- Suggest improvements
- Contribute example prompts
- Report bugs or limitations

Remember: The best learning happens when students struggle *just enough* - Vibescriptor helps find that sweet spot!
