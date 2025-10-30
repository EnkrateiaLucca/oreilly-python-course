# Improved Automation Scripts

This folder contains 5 practical and well-designed automation scripts that address common real-world needs. Each script is self-contained, uses modern Python patterns with uv script metadata, and includes proper error handling.

## Scripts Overview

### 1. Smart File Organizer (`smart_file_organizer.py`)
**Problem Solved:** Messy directories with mixed file types

**Features:**
- Organize files by type (Documents, Images, Videos, etc.)
- Organize files by date (Year/Month structure)
- Organize files by size categories
- Dry-run mode to preview changes
- Handles duplicate filenames automatically
- Beautiful terminal output with statistics

**Usage:**
```bash
# Organize current directory by type
python smart_file_organizer.py

# Organize Downloads folder by date
python smart_file_organizer.py ~/Downloads --mode=date

# Preview organization without moving files
python smart_file_organizer.py ~/Desktop --mode=type --dry-run

# Organize by file size
python smart_file_organizer.py ~/Documents --mode=size
```

**Why Better:**
- Multiple organization strategies in one tool
- Safer with dry-run preview
- No hardcoded paths
- Clear visual feedback

---

### 2. Duplicate File Finder (`duplicate_file_finder.py`)
**Problem Solved:** Wasted disk space from duplicate files

**Features:**
- Find duplicates based on content hash (not just name)
- Shows wasted space per duplicate set
- Multiple deletion strategies (keep oldest/newest/first)
- Export report to text file
- Recursive scanning
- Keeps oldest file by default (safer)

**Usage:**
```bash
# Find duplicates in current directory
python duplicate_file_finder.py

# Find duplicates recursively in Downloads
python duplicate_file_finder.py ~/Downloads --recursive

# Delete duplicates (will ask for confirmation)
python duplicate_file_finder.py ~/Pictures --delete

# Delete duplicates, keeping newest files
python duplicate_file_finder.py ~/Documents --delete --keep=newest

# Export report without deleting
python duplicate_file_finder.py ~/Desktop --export=duplicates_report.txt
```

**Why Better:**
- Content-based detection (catches renamed duplicates)
- Safe deletion with confirmation
- Shows space savings before deleting
- Configurable keep strategy

---

### 3. Batch Image Processor (`batch_image_processor.py`)
**Problem Solved:** Need to resize/convert/compress multiple images

**Features:**
- Bulk resize with aspect ratio preservation
- Format conversion (JPG, PNG, WebP, etc.)
- Quality/compression control
- Add text watermarks
- Handles RGBA → RGB conversion automatically
- Shows space savings

**Usage:**
```bash
# Resize all images to max 1920x1080
python batch_image_processor.py ~/Pictures/Vacation --resize 1920x1080

# Convert all images to WebP format
python batch_image_processor.py ~/Pictures --format webp

# Compress images with custom quality
python batch_image_processor.py ~/Desktop --format jpg --quality 75

# Add watermark to all images
python batch_image_processor.py ~/Photos --watermark "© 2024 My Name"

# Complex: resize, convert, compress, and watermark
python batch_image_processor.py ~/Photos \
  --resize 2560x1440 \
  --format jpg \
  --quality 85 \
  --watermark "© My Portfolio" \
  --watermark-position bottom-right

# Process subdirectories recursively
python batch_image_processor.py ~/Pictures --recursive --resize 1920x1080
```

**Why Better:**
- All-in-one image processing tool
- Maintains image quality intelligently
- Shows before/after statistics
- Handles format conversions properly (RGBA/RGB)

---

### 4. Website Monitor (`website_monitor.py`)
**Problem Solved:** Need to track changes on websites (prices, content, availability)

**Features:**
- Monitor multiple websites
- CSS selector support for specific elements
- Change detection via content hashing
- Continuous monitoring mode
- History tracking
- Alert on changes
- Configurable check intervals

**Usage:**
```bash
# Add a site to monitor
python website_monitor.py add \
  --name "Product Price" \
  --url "https://example.com/product" \
  --selector ".price" \
  --interval 300

# List all monitored sites
python website_monitor.py list

# Check all sites once
python website_monitor.py check

# Start continuous monitoring (every 5 minutes)
python website_monitor.py monitor --interval 300

# View monitoring history
python website_monitor.py history

# View history for specific site
python website_monitor.py history --name "Product Price" --limit 20

# Remove a site
python website_monitor.py remove "Product Price"
```

**Use Cases:**
- Monitor product prices
- Track stock availability
- Watch for website updates
- Monitor competitor content
- Track job postings

**Why Better:**
- Persistent configuration (saves to JSON)
- Supports CSS selectors for precise monitoring
- Built-in history tracking
- Continuous monitoring mode
- Much more flexible than existing scripts

---

### 5. Git Repo Analyzer (`git_repo_analyzer.py`)
**Problem Solved:** Understanding repository health, activity, and structure

**Features:**
- Comprehensive commit statistics
- Author contribution analysis
- File type breakdown and sizes
- Activity patterns (by day/hour)
- Branch information
- Find largest files
- Commit frequency graphs
- Export analysis to JSON

**Usage:**
```bash
# Analyze current repository
python git_repo_analyzer.py

# Analyze specific repository
python git_repo_analyzer.py ~/projects/my-app

# Analyze last 90 days of activity
python git_repo_analyzer.py ~/projects/my-app --days 90

# Export analysis to JSON
python git_repo_analyzer.py . --export=repo_analysis.json
```

**Insights Provided:**
- Who are the top contributors?
- What file types dominate the codebase?
- When is the team most active?
- Which branches are stale?
- What are the largest files?
- How many lines of code?
- Commit patterns over time

**Why Better:**
- Rich visual output
- Much more comprehensive than simple stats
- Helpful for code reviews and audits
- Identifies technical debt (large files, stale branches)

---

## Key Improvements Over Original Scripts

### 1. **Better Structure**
- Clear separation of concerns
- Reusable functions
- Class-based for complex tools

### 2. **Practical & Universal**
- No hardcoded paths
- Configurable via CLI arguments
- Works on any system

### 3. **Modern Python**
- Type hints
- uv script metadata
- Rich terminal output
- Proper error handling

### 4. **User-Friendly**
- Clear help messages
- Preview/dry-run modes
- Progress indicators
- Confirmation prompts for dangerous operations

### 5. **Production-Ready**
- Handles edge cases (duplicates, permissions, etc.)
- Resource-efficient (streaming, chunking)
- Detailed feedback and statistics

## Running the Scripts

All scripts use uv for dependency management. They can be run directly:

```bash
# Make executable
chmod +x smart_file_organizer.py

# Run directly
./smart_file_organizer.py --help

# Or with uv explicitly
uv run smart_file_organizer.py --help
```

## Comparison with Original Scripts

| Original | Issue | Improved Version |
|----------|-------|------------------|
| `organize_table_of_downloads_folder.py` | Too complex, creates 6 visualizations | `smart_file_organizer.py` - Simpler, faster, more practical |
| `file_backup_reorg.py` | Hardcoded paths, no flexibility | `smart_file_organizer.py` - Configurable, multiple modes |
| `get_popular_reviews.py` | Too specific to Letterboxd | `website_monitor.py` - Generic website monitoring |
| Various scripts | No duplicate detection | `duplicate_file_finder.py` - Finds wasted space |
| Image scripts | Missing batch processing | `batch_image_processor.py` - Complete image toolkit |

## Next Steps

1. Test each script on your actual use cases
2. Customize default values in the code if needed
3. Create shell aliases for frequently used commands
4. Consider adding email/webhook notifications to website monitor
5. Extend git analyzer with more metrics as needed
