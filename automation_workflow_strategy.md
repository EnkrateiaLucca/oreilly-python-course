# Automation Workflow Strategy
## O'Reilly Live Training - Automate Tasks with Python + AI

### Executive Summary

This document outlines a comprehensive automation strategy for the O'Reilly Python + AI automation course. The strategy leverages Python's ecosystem, modern tooling (UV package manager), and AI APIs to create efficient, maintainable automation workflows suitable for teaching and real-world application.

---

## 1. Project Scope & Goals

### Current State
- **Course Type**: Live training focused on teaching automation with Python and AI
- **Target Audience**: Beginners to intermediate Python users
- **Key Technologies**: Python 3.13+, Jupyter Lab, OpenAI, Anthropic Claude, Ollama
- **Structure**: Progressive learning from fundamentals → AI APIs → automation projects

### Core Learning Objectives
1. Master Python fundamentals for automation
2. Integrate AI APIs effectively into workflows
3. Build practical automation solutions
4. Develop maintainable, reusable automation scripts
5. Understand modern Python tooling and best practices

---

## 2. Automation Architecture Strategy

### 2.1 Three-Tier Automation Approach

#### **Tier 1: Notebook-Based Exploration (Learning Phase)**
- **Purpose**: Interactive learning and experimentation
- **Location**: `notebooks/` directory
- **Best For**:
  - Teaching concepts
  - Iterative development
  - Data exploration
  - Prototyping automation ideas

#### **Tier 2: Standalone Scripts (Production Phase)**
- **Purpose**: Reusable, executable automation tools
- **Location**: `scripts/` directory
- **Best For**:
  - Production automation
  - Scheduled tasks
  - CLI tools
  - Integration with other systems

#### **Tier 3: Modular Libraries (Scale Phase)**
- **Purpose**: Shared utilities and frameworks
- **Current Example**: `scripts/ai_tools.py`
- **Best For**:
  - Code reuse across projects
  - Standardized interfaces
  - Testing and maintenance

---

## 3. Key Automation Patterns Identified

### 3.1 UV Script Pattern (Recommended Standard)

**Why UV Scripts?**
- Zero setup required (dependencies in script header)
- Reproducible execution environments
- No manual virtual environment management
- Perfect for distributing automation tools

**Implementation Pattern**:
```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests",
#     "pandas",
#     "rich"
# ]
# ///

# Your automation code here
```

**Current Examples**:
- `scripts/file_backup_reorg.py` - File organization
- `scripts/extract_data_from_pdf.py` - Data extraction
- `scripts/ppt_financial.py` - Presentation generation
- `scripts/organize_table_of_downloads_folder.py` - Advanced file analysis

**Recommendation**: Make this the PRIMARY pattern for all production scripts in the course.

---

### 3.2 AI Integration Pattern

**Current Implementation**: `scripts/ai_tools.py`

**Strengths**:
- Unified interface for multiple AI providers (OpenAI, Anthropic, Ollama)
- Simple `ask_ai()` function abstracts complexity
- Supports structured outputs (JSON)
- Handles local and cloud-based models

**Enhancement Opportunities**:

1. **Add Error Handling & Retry Logic**
```python
def ask_ai(prompt, model_name="gpt-4o-mini", max_retries=3):
    for attempt in range(max_retries):
        try:
            # existing code
            return output
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # exponential backoff
```

2. **Add Streaming Support**
```python
def ask_ai_stream(prompt, model_name="gpt-4o-mini"):
    """Stream responses for long-running AI tasks"""
    # Implementation for streaming responses
```

3. **Add Token/Cost Tracking**
```python
def ask_ai_with_metrics(prompt, model_name="gpt-4o-mini"):
    """Return response with token usage and cost metrics"""
    # Track usage for course demonstrations
```

---

### 3.3 File System Automation Pattern

**Examples**:
- `scripts/file_backup_reorg.py` - Structured backup with date prefixes
- `scripts/organize_table_of_downloads_folder.py` - Comprehensive file analysis

**Key Features**:
- Recursive directory traversal
- Metadata extraction (size, date, type)
- Rich console output for user feedback
- Data persistence (CSV exports)
- Visualization generation

**Best Practices**:
- Always use `os.makedirs(path, exist_ok=True)` for directory creation
- Implement depth limiting for large directory trees
- Include progress indicators for long operations
- Generate reports/summaries for audit trails

---

### 3.4 Data Processing & Visualization Pattern

**Example**: `scripts/organize_table_of_downloads_folder.py`

**Strengths**:
- Pandas for data manipulation
- Multiple visualization libraries (matplotlib, seaborn, plotly)
- Rich terminal UI for immediate feedback
- Export capabilities (CSV, PNG)

**Pattern Template**:
```python
1. Data Collection → DataFrame
2. Data Analysis → Aggregations/Summaries
3. Visualization → Charts/Graphs
4. Output Generation → Files/Reports
5. User Feedback → Rich console display
```

---

### 3.5 AI-Enhanced Automation Pattern

**Current Examples**:
- `scripts/extract_data_from_pdf.py` - Traditional extraction
- Notebook examples showing AI-enhanced extraction

**Enhancement Strategy**:

Combine traditional extraction with AI:
```python
def smart_data_extraction(file_path):
    # 1. Traditional extraction (fast, structured)
    raw_data = extract_with_pypdf(file_path)

    # 2. AI enhancement (intelligent parsing)
    structured_data = ask_ai(
        f"Extract key information from: {raw_data}",
        structured=True
    )

    # 3. Validation & cleanup
    return validate_and_clean(structured_data)
```

---

## 4. Recommended Automation Workflows

### 4.1 Content Management Workflow

**Purpose**: Manage course materials and student resources

**Automation Opportunities**:

1. **Notebook Conversion Pipeline**
   - Convert markdown → Jupyter notebooks
   - Existing: `scripts/markdown_to_jupyter.py`
   - Enhancement: Add cell metadata, execution order, tags

2. **Resource Organization**
   - Auto-organize assets by module
   - Generate index files
   - Create resource manifests

3. **Backup & Version Control**
   - Scheduled backups with timestamps
   - Existing: `scripts/file_backup_reorg.py`
   - Enhancement: Git integration, incremental backups

**Implementation Example**:
```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["watchdog", "gitpython"]
# ///

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class NotebookWatcher(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.ipynb'):
            # Auto-backup on save
            backup_notebook(event.src_path)
            # Run quality checks
            validate_notebook(event.src_path)
```

---

### 4.2 Presentation Generation Workflow

**Purpose**: Automate slide creation from data and code

**Current Implementation**: `scripts/ppt_financial.py`

**Strengths**:
- Reads Excel data files
- Generates charts automatically
- Creates PowerPoint presentations
- Handles multiple data sheets/stocks

**Enhancement Strategy**:

1. **Template System**
```python
# Create presentation template library
templates = {
    'financial': load_template('financial.pptx'),
    'technical': load_template('technical.pptx'),
    'educational': load_template('educational.pptx')
}
```

2. **AI-Powered Slide Content**
```python
def generate_slide_narrative(chart_data):
    prompt = f"""
    Analyze this data: {chart_data}
    Generate:
    1. Title (10 words)
    2. Key insights (3 bullet points)
    3. Recommendation (2 sentences)
    """
    return ask_ai(prompt, structured=True)
```

3. **Batch Processing**
```python
def process_all_inputs(input_folder):
    for file in glob(f"{input_folder}/*.xlsx"):
        ppt = generate_presentation(file)
        ppt.save(f"output/{Path(file).stem}_slides.pptx")
```

---

### 4.3 Web Automation Workflow

**Purpose**: Automate browser interactions and data collection

**Current Implementation**: Playwright scripts

**Examples**:
- `scripts/github_info_fetch.py` - Repository interaction
- `scripts/letterboxd_saving_auth_browser.py` - Authenticated browsing
- `scripts/add_movie_to_watchlist.py` - Form automation

**Best Practices**:

1. **Reusable Browser Context**
```python
def get_browser_context(headless=True, save_auth=False):
    """Reusable browser setup with optional auth persistence"""
    browser = playwright.chromium.launch(headless=headless)
    if save_auth:
        context = browser.new_context(storage_state="auth.json")
    else:
        context = browser.new_context()
    return browser, context
```

2. **Error Handling & Retries**
```python
def robust_click(page, selector, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            page.wait_for_selector(selector, timeout=5000)
            page.click(selector)
            return True
        except:
            if attempt == max_attempts - 1:
                raise
            time.sleep(1)
```

3. **Data Extraction Pattern**
```python
def scrape_with_fallback(url):
    # Try API first (fastest)
    if has_api(url):
        return fetch_from_api(url)

    # Fall back to web scraping
    return scrape_with_playwright(url)
```

---

### 4.4 Data Extraction & Processing Workflow

**Purpose**: Extract, transform, and analyze data from various sources

**Current Examples**:
- PDF extraction (`extract_data_from_pdf.py`)
- Web data extraction (notebooks)
- Receipt/invoice processing (notebooks)

**Enhanced Pattern**:

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pymupdf", "pdfplumber", "anthropic", "pandas"]
# ///

class SmartExtractor:
    def __init__(self):
        self.extractors = {
            'pdf': self.extract_pdf,
            'image': self.extract_image,
            'web': self.extract_web
        }

    def extract(self, source_path, output_format='json'):
        # 1. Detect source type
        source_type = self.detect_type(source_path)

        # 2. Use appropriate extractor
        raw_data = self.extractors[source_type](source_path)

        # 3. AI-enhanced structuring
        structured = self.ai_structure(raw_data)

        # 4. Format conversion
        return self.format_output(structured, output_format)

    def ai_structure(self, raw_data):
        """Use AI to intelligently parse unstructured data"""
        prompt = f"""
        Extract structured data from:
        {raw_data}

        Return JSON with keys: title, date, amounts, categories
        """
        return ask_ai(prompt, structured=True)
```

---

### 4.5 Email & Communication Workflow

**Purpose**: Automate email processing and communication tasks

**Current**: Notebook examples (`08-email-assistant.ipynb`)

**Production Pattern**:

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["imap-tools", "anthropic", "jinja2"]
# ///

class EmailAutomation:
    def process_inbox(self):
        # 1. Fetch emails
        emails = self.fetch_unread_emails()

        # 2. AI classification
        for email in emails:
            category = self.classify_email(email)

            # 3. Automated actions
            if category == 'urgent':
                self.send_notification(email)
            elif category == 'receipt':
                self.extract_and_log(email)
            elif category == 'newsletter':
                self.archive(email)

    def classify_email(self, email):
        """Use AI to categorize email"""
        return ask_ai(
            f"Categorize this email: {email.subject}\n{email.body[:500]}",
            model_name="gpt-4o-mini"
        )

    def generate_response(self, email, tone='professional'):
        """AI-powered email response generation"""
        template = load_template(f'response_{tone}.jinja2')
        context = ask_ai(f"Draft response to: {email.body}")
        return template.render(context=context)
```

---

## 5. Tooling & Infrastructure Strategy

### 5.1 Package Management

**Current**: UV package manager ✅

**Advantages**:
- Fast installation
- Built-in script running (`uv run`)
- Lock files for reproducibility
- Works with standard `pyproject.toml`

**Recommendation**: Continue using UV as the primary package manager

**Best Practices**:
```bash
# Install dependencies
uv pip install <package>

# Run scripts
uv run scripts/my_script.py

# Sync environment
uv sync
```

---

### 5.2 Development Environment

**Current Setup**:
- Python 3.13
- Jupyter Lab for interactive work
- IPython kernel for notebooks
- Rich library for enhanced CLI output

**Enhancements**:

1. **Add Development Tools**
```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "black>=24.0.0",
    "ruff>=0.1.0",
    "ipytest>=0.14.0"  # Testing in notebooks
]
```

2. **Pre-commit Hooks**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        language_version: python3.13

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
```

3. **Testing Strategy**
```python
# scripts/tests/test_ai_tools.py
import pytest
from scripts.ai_tools import ask_ai, parse_json_output

def test_parse_json_output():
    input_str = '```json\n{"key": "value"}\n```'
    result = parse_json_output(input_str)
    assert result == {"key": "value"}

def test_ask_ai_mock():
    # Use mock for testing
    result = ask_ai("test prompt", model_name="mock")
    assert isinstance(result, str)
```

---

### 5.3 Configuration Management

**Current Gap**: No centralized configuration

**Recommendation**: Implement configuration pattern

```python
# scripts/config.py
from pathlib import Path
from dataclasses import dataclass
import os

@dataclass
class Config:
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Paths
    project_root: Path = Path(__file__).parent.parent
    assets_dir: Path = project_root / "assets"
    notebooks_dir: Path = project_root / "notebooks"
    scripts_dir: Path = project_root / "scripts"

    # AI Settings
    default_model: str = "gpt-4o-mini"
    max_tokens: int = 4000
    temperature: float = 0.7

    @classmethod
    def from_env(cls):
        """Load configuration from environment"""
        return cls()

# Usage in scripts
config = Config.from_env()
```

---

### 5.4 Logging & Monitoring

**Current Gap**: Minimal logging

**Recommendation**: Implement structured logging

```python
# scripts/logger.py
import logging
from rich.logging import RichHandler

def setup_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Rich handler for beautiful console output
    console_handler = RichHandler(rich_tracebacks=True)
    console_handler.setFormatter(
        logging.Formatter("%(message)s")
    )

    # File handler for persistence
    file_handler = logging.FileHandler('automation.log')
    file_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    )

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# Usage
from logger import setup_logger
logger = setup_logger(__name__)
logger.info("Starting automation")
```

---

## 6. Course-Specific Automation Recommendations

### 6.1 Automated Exercise Generation

**Problem**: Creating varied practice exercises manually

**Solution**: AI-powered exercise generator

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["anthropic", "nbformat"]
# ///

def generate_exercise_notebook(topic, difficulty, num_problems=5):
    """Generate practice exercises automatically"""

    prompt = f"""
    Create {num_problems} Python exercises for: {topic}
    Difficulty: {difficulty}

    For each exercise provide:
    1. Problem statement
    2. Starter code
    3. Test cases
    4. Solution (in separate cell)

    Format as Jupyter notebook JSON.
    """

    notebook_json = ask_ai(prompt, structured=True)
    save_notebook(notebook_json, f"exercise_{topic}_{difficulty}.ipynb")
```

---

### 6.2 Student Progress Tracking

**Problem**: Tracking student completion and understanding

**Solution**: Automated analytics from notebook execution

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["nbformat", "pandas", "plotly"]
# ///

def analyze_student_notebooks(notebook_dir):
    """Analyze notebook execution patterns"""

    metrics = []
    for notebook_path in Path(notebook_dir).glob("**/*.ipynb"):
        nb = nbformat.read(notebook_path, as_version=4)

        metrics.append({
            'notebook': notebook_path.name,
            'cells_executed': count_executed_cells(nb),
            'errors': count_errors(nb),
            'completion_time': estimate_time(nb),
            'last_modified': notebook_path.stat().st_mtime
        })

    df = pd.DataFrame(metrics)
    generate_progress_report(df)
```

---

### 6.3 Live Demo Automation

**Problem**: Setting up demos during live training

**Solution**: One-command demo setup

```bash
#!/usr/bin/env bash
# setup-demo.sh

# Quick demo setup script
DEMO_TYPE=$1

case $DEMO_TYPE in
  "file-automation")
    uv run scripts/organize_table_of_downloads_folder.py
    ;;
  "ai-extraction")
    uv run scripts/extract_data_from_pdf.py demo.pdf
    ;;
  "web-scraping")
    uv run scripts/github_info_fetch.py
    ;;
  "presentation")
    uv run scripts/ppt_financial.py
    ;;
  *)
    echo "Usage: ./setup-demo.sh [file-automation|ai-extraction|web-scraping|presentation]"
    ;;
esac
```

---

### 6.4 Resource Management Automation

**Problem**: Managing sample data and assets

**Solution**: Automated asset management

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["requests", "rich"]
# ///

class AssetManager:
    """Manage course assets and sample data"""

    def setup_module_assets(self, module_name):
        """Download and organize assets for a module"""

        assets_config = self.load_config(f"config/{module_name}.yaml")

        for asset in assets_config['required_files']:
            if not self.asset_exists(asset):
                self.download_asset(asset)

        self.verify_all_assets(module_name)

    def generate_sample_data(self, data_type, size='medium'):
        """Generate sample data for exercises"""

        generators = {
            'csv': self.generate_csv,
            'json': self.generate_json,
            'pdf': self.generate_pdf
        }

        return generators[data_type](size)
```

---

## 7. Best Practices & Guidelines

### 7.1 Script Design Principles

1. **Single Responsibility**
   - Each script does one thing well
   - Compose complex workflows from simple scripts

2. **UV Script Headers**
   - Always include dependency specifications
   - Pin Python version requirements
   - Document required environment variables

3. **User Feedback**
   - Use Rich library for enhanced output
   - Show progress bars for long operations
   - Provide clear error messages

4. **Configuration**
   - Use environment variables for secrets
   - Use config files for preferences
   - Provide sensible defaults

5. **Error Handling**
   - Fail gracefully with helpful messages
   - Log errors for debugging
   - Implement retry logic where appropriate

---

### 7.2 AI Integration Best Practices

1. **Cost Management**
   - Use cheaper models (gpt-4o-mini) for simple tasks
   - Cache repeated queries
   - Implement token limits

2. **Prompt Engineering**
   - Be specific about output format
   - Provide examples in prompts
   - Use structured outputs (JSON)

3. **Fallback Strategies**
   - Support multiple AI providers
   - Have non-AI fallbacks where possible
   - Handle API failures gracefully

4. **Local vs Cloud**
   - Use Ollama for development/testing
   - Use cloud APIs for production quality
   - Allow users to choose

---

### 7.3 Code Organization

**Recommended Structure**:
```
project-root/
├── scripts/              # Production automation scripts
│   ├── __init__.py
│   ├── ai_tools.py      # Shared AI utilities
│   ├── config.py        # Configuration management
│   ├── logger.py        # Logging utilities
│   └── automation_*.py  # Specific automation scripts
│
├── notebooks/           # Teaching & exploration
│   ├── 01-fundamentals/
│   ├── 02-ai-apis/
│   ├── 03-automation-projects/
│   └── 04-exercises/
│
├── assets/              # Sample data & resources
│   ├── data/
│   ├── images/
│   └── templates/
│
├── tests/               # Automated tests
│   ├── test_ai_tools.py
│   └── test_scripts.py
│
├── config/              # Configuration files
│   └── defaults.yaml
│
├── .env.example         # Template for API keys
├── pyproject.toml       # Project dependencies
└── uv.lock             # Lock file for reproducibility
```

---

## 8. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- ✅ Set up UV package management
- ✅ Create core utility modules (ai_tools.py)
- ✅ Establish UV script pattern
- 🔄 Add configuration management
- 🔄 Implement logging infrastructure

### Phase 2: Core Automations (Week 3-4)
- ✅ File management automation
- ✅ PDF data extraction
- ✅ Presentation generation
- ✅ Web scraping examples
- 🔄 Email automation
- 🔄 Scheduler agent

### Phase 3: Enhancement (Week 5-6)
- 🔄 Add error handling & retries
- 🔄 Implement testing framework
- 🔄 Create demo setup scripts
- 🔄 Build asset management system
- 🔄 Add progress tracking

### Phase 4: Polish (Week 7-8)
- 🔄 Documentation generation
- 🔄 Exercise auto-generation
- 🔄 Student analytics
- 🔄 Performance optimization
- 🔄 Course delivery automation

---

## 9. Quick Win Automations

### 9.1 Immediate Opportunities

1. **Notebook Quality Checker**
```python
# Check notebooks for common issues before class
- Empty cells
- Missing outputs
- Broken image links
- Outdated package versions
```

2. **Environment Validator**
```python
# Verify student environments are set up correctly
- Python version
- Required packages
- API keys configured
- Jupyter kernel installed
```

3. **Demo Reset Script**
```python
# Reset environment between demos
- Clear output folders
- Reset sample data
- Clean temp files
- Restart Jupyter kernels
```

4. **Resource Packager**
```python
# Package module resources for distribution
- Collect all required files
- Generate checksums
- Create zip archive
- Upload to hosting
```

---

## 10. Metrics & Success Criteria

### Automation Effectiveness Metrics

1. **Time Savings**
   - Manual task time vs automated
   - Setup time reduction
   - Demo preparation time

2. **Reliability**
   - Success rate of automated tasks
   - Error frequency
   - Recovery time

3. **Maintainability**
   - Code reuse percentage
   - Update frequency required
   - Bug fix time

4. **Student Experience**
   - Setup completion rate
   - Exercise completion time
   - Feedback scores

---

## 11. Future Enhancements

### 11.1 Advanced AI Integration

1. **AI Code Review Assistant**
```python
def review_student_code(notebook_path):
    """Provide automated feedback on student code"""
    code = extract_code_cells(notebook_path)

    feedback = ask_ai(f"""
    Review this Python code for:
    1. Correctness
    2. Best practices
    3. Potential improvements
    4. Security issues

    Code: {code}
    """, model_name="claude-3-5-sonnet")

    return structured_feedback(feedback)
```

2. **Intelligent Exercise Difficulty Adjustment**
```python
def adjust_exercise_difficulty(student_history):
    """Dynamically adjust exercise difficulty based on performance"""
    # Analyze past performance
    # Generate appropriate challenges
    # Track learning progression
```

3. **Natural Language Automation Builder**
```python
def build_automation_from_description(description):
    """Generate automation script from natural language"""

    prompt = f"""
    Create a Python automation script for:
    {description}

    Include:
    - UV script header
    - Error handling
    - Progress feedback
    - Documentation
    """

    return ask_ai(prompt, model_name="claude-3-5-sonnet")
```

---

### 11.2 Platform Integrations

1. **GitHub Integration**
   - Auto-create repositories for students
   - Automated PR reviews
   - Issue tracking for questions

2. **Slack/Discord Bots**
   - Course announcements
   - Q&A automation
   - Resource sharing

3. **Learning Management Systems**
   - Grade synchronization
   - Progress tracking
   - Certificate generation

---

## 12. Conclusion

### Key Takeaways

1. **UV Script Pattern**: Adopt as the standard for all production automation scripts
2. **Three-Tier Approach**: Notebooks for learning, scripts for production, libraries for scale
3. **AI-Enhanced**: Combine traditional automation with AI for intelligent processing
4. **Modular Design**: Build reusable components that compose into workflows
5. **Student-Centric**: Automate course management to focus on teaching

### Success Factors

- **Simplicity**: Keep individual scripts focused and simple
- **Reusability**: Build once, use many times
- **Maintainability**: Clear code, good documentation, proper testing
- **Flexibility**: Support multiple AI providers and fallback strategies
- **Observability**: Logging, monitoring, and feedback loops

### Next Steps

1. Implement core utilities (config, logging)
2. Standardize all scripts with UV pattern
3. Add comprehensive error handling
4. Create testing infrastructure
5. Build course-specific automation tools
6. Document patterns and best practices
7. Gather feedback and iterate

---

## Appendix: Reference Scripts

### A. Template UV Script

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "anthropic",
#     "pandas",
#     "rich"
# ]
# ///
"""
Script Purpose: [Brief description]
Author: [Name]
Date: [Date]
Usage: uv run script_name.py [arguments]
"""

from rich.console import Console
from scripts.ai_tools import ask_ai
from scripts.config import Config
from scripts.logger import setup_logger

# Setup
console = Console()
logger = setup_logger(__name__)
config = Config.from_env()

def main():
    """Main automation logic"""
    try:
        logger.info("Starting automation")

        # Your automation code here

        console.print("[green]✅ Automation completed successfully[/green]")

    except Exception as e:
        logger.error(f"Automation failed: {e}")
        console.print(f"[red]❌ Error: {e}[/red]")
        raise

if __name__ == "__main__":
    main()
```

### B. Template Testing Script

```python
# tests/test_automation.py
import pytest
from pathlib import Path
from scripts.automation_script import main, process_data

@pytest.fixture
def sample_data():
    """Provide sample data for testing"""
    return {
        'key': 'value',
        'items': [1, 2, 3]
    }

def test_process_data(sample_data):
    """Test data processing function"""
    result = process_data(sample_data)
    assert result is not None
    assert 'processed' in result

def test_main_execution(tmp_path):
    """Test main function execution"""
    # Setup test environment
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    # Run automation
    result = main(input_path=str(test_file))

    # Verify results
    assert result['success'] == True
```

---

**Document Version**: 1.0
**Last Updated**: 2025-10-30
**Author**: Automation Analysis AI
**Status**: Ready for Implementation
