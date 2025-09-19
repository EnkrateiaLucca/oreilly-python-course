# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "pandas",
#     "pathlib",
#     "shutil",
#     "magic",
#     "difflib",
#     "textdistance",
#     "chardet",
#     "pillow",
#     "PyPDF2",
# ]
# ///

"""
LA File Organizer
Student: LA
Description: Go over files and 1. classify them into folders 2. create an index to find files
3. create resume of specific file 4. compare side by side 2-3 file text

This script demonstrates how to:
1. Automatically classify and organize files by type and content
2. Create searchable indexes for quick file location
3. Generate summaries/resumes of file contents
4. Compare multiple files side by side with difference highlighting
5. Handle various file formats (text, images, PDFs, etc.)

Educational Focus:
- File system operations and organization
- Content analysis and classification
- Text processing and summarization
- File comparison algorithms
- Index creation and searching
- Working with multiple file formats
"""

import os
import shutil
from pathlib import Path
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd
import difflib
import re
from collections import defaultdict, Counter
import chardet

# For file type detection
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False
    print("⚠️  python-magic not available. Using basic file type detection.")

# For text similarity
try:
    import textdistance
    HAS_TEXTDISTANCE = True
except ImportError:
    HAS_TEXTDISTANCE = False

# For image handling
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# For PDF handling
try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

class FileClassifier:
    """
    Intelligently classifies files based on content, type, and naming patterns
    """

    def __init__(self):
        """Initialize the file classifier with category definitions"""

        # Define file categories with extensions and keywords
        self.categories = {
            'documents': {
                'extensions': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
                'keywords': ['document', 'report', 'letter', 'memo', 'contract'],
                'folder': 'Documents'
            },
            'spreadsheets': {
                'extensions': ['.xls', '.xlsx', '.csv', '.ods'],
                'keywords': ['data', 'spreadsheet', 'budget', 'inventory', 'list'],
                'folder': 'Spreadsheets'
            },
            'presentations': {
                'extensions': ['.ppt', '.pptx', '.odp'],
                'keywords': ['presentation', 'slides', 'deck'],
                'folder': 'Presentations'
            },
            'images': {
                'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg'],
                'keywords': ['photo', 'image', 'picture', 'screenshot'],
                'folder': 'Images'
            },
            'code': {
                'extensions': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.rb', '.php'],
                'keywords': ['script', 'code', 'program', 'source'],
                'folder': 'Code'
            },
            'archives': {
                'extensions': ['.zip', '.rar', '.7z', '.tar', '.gz'],
                'keywords': ['archive', 'backup', 'compressed'],
                'folder': 'Archives'
            },
            'media': {
                'extensions': ['.mp4', '.avi', '.mkv', '.mp3', '.wav', '.flac'],
                'keywords': ['video', 'audio', 'music', 'movie'],
                'folder': 'Media'
            },
            'projects': {
                'extensions': [],
                'keywords': ['project', 'work', 'assignment'],
                'folder': 'Projects'
            }
        }

        # If magic is available, initialize it
        if HAS_MAGIC:
            try:
                self.magic = magic.Magic(mime=True)
            except:
                self.magic = None
        else:
            self.magic = None

        print("✅ File Classifier initialized")

    def classify_file(self, file_path: Path) -> str:
        """
        Classify a file into one of the predefined categories

        Args:
            file_path: Path to the file to classify

        Returns:
            Category name for the file
        """
        file_name = file_path.name.lower()
        file_ext = file_path.suffix.lower()

        # First, try classification by extension
        for category, details in self.categories.items():
            if file_ext in details['extensions']:
                return category

        # Then try classification by filename keywords
        for category, details in self.categories.items():
            for keyword in details['keywords']:
                if keyword in file_name:
                    return category

        # For text files, try content-based classification
        if file_ext in ['.txt', '.md', ''] and file_path.is_file():
            content_category = self._classify_by_content(file_path)
            if content_category:
                return content_category

        # If magic is available, try MIME type classification
        if self.magic and file_path.is_file():
            try:
                mime_type = self.magic.from_file(str(file_path))
                mime_category = self._classify_by_mime(mime_type)
                if mime_category:
                    return mime_category
            except:
                pass

        # Default category
        return 'miscellaneous'

    def _classify_by_content(self, file_path: Path) -> Optional[str]:
        """Classify text files based on their content"""
        try:
            # Read a sample of the file to determine encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read(1024)

            encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'

            # Read the file content
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                content = f.read(2000).lower()  # Read first 2000 chars

            # Check for code patterns
            code_patterns = [
                r'def\s+\w+\s*\(',  # Python functions
                r'function\s+\w+\s*\(',  # JavaScript functions
                r'class\s+\w+',  # Class definitions
                r'import\s+\w+',  # Import statements
                r'#include\s*<',  # C/C++ includes
                r'<?php',  # PHP tags
            ]

            for pattern in code_patterns:
                if re.search(pattern, content):
                    return 'code'

            # Check for document patterns
            doc_patterns = [
                r'\b(dear|sincerely|regards)\b',  # Letter patterns
                r'\b(introduction|conclusion|summary)\b',  # Document structure
                r'\b(chapter|section|appendix)\b',  # Book/report structure
            ]

            for pattern in doc_patterns:
                if re.search(pattern, content):
                    return 'documents'

            return None

        except Exception:
            return None

    def _classify_by_mime(self, mime_type: str) -> Optional[str]:
        """Classify files based on MIME type"""
        mime_mappings = {
            'text/': 'documents',
            'image/': 'images',
            'video/': 'media',
            'audio/': 'media',
            'application/pdf': 'documents',
            'application/msword': 'documents',
            'application/vnd.ms-excel': 'spreadsheets',
            'application/vnd.ms-powerpoint': 'presentations',
            'application/zip': 'archives',
        }

        for mime_prefix, category in mime_mappings.items():
            if mime_type.startswith(mime_prefix):
                return category

        return None

class FileOrganizer:
    """
    Organizes files into categorized folder structures
    """

    def __init__(self, base_directory: Path):
        """
        Initialize the file organizer

        Args:
            base_directory: Base directory to organize files in
        """
        self.base_dir = Path(base_directory)
        self.classifier = FileClassifier()
        self.organization_log = []

        print(f"✅ File Organizer initialized for: {self.base_dir}")

    def organize_files(self, source_directory: Path = None, dry_run: bool = True) -> Dict[str, Any]:
        """
        Organize files in the specified directory

        Args:
            source_directory: Directory to organize (defaults to base_directory)
            dry_run: If True, only plan the organization without moving files

        Returns:
            Dictionary with organization results and statistics
        """
        if source_directory is None:
            source_directory = self.base_dir

        source_path = Path(source_directory)

        if not source_path.exists():
            print(f"❌ Source directory does not exist: {source_path}")
            return {}

        print(f"📁 {'Planning' if dry_run else 'Executing'} file organization in: {source_path}")

        # Find all files to organize
        files_to_organize = []
        for file_path in source_path.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                files_to_organize.append(file_path)

        print(f"🔍 Found {len(files_to_organize)} files to organize")

        # Classify and plan organization
        organization_plan = defaultdict(list)
        for file_path in files_to_organize:
            category = self.classifier.classify_file(file_path)
            organization_plan[category].append(file_path)

        # Execute organization plan
        results = {
            'total_files': len(files_to_organize),
            'categories': dict(organization_plan),
            'moved_files': 0,
            'errors': []
        }

        if not dry_run:
            results['moved_files'] = self._execute_organization_plan(organization_plan)
        else:
            print("\n📋 Organization Plan (Dry Run):")
            for category, files in organization_plan.items():
                folder_name = self.classifier.categories.get(category, {}).get('folder', category.title())
                print(f"  {folder_name}: {len(files)} files")

        return results

    def _execute_organization_plan(self, organization_plan: Dict[str, List[Path]]) -> int:
        """Execute the file organization plan"""
        moved_count = 0

        for category, files in organization_plan.items():
            if not files:
                continue

            # Create category folder
            folder_name = self.classifier.categories.get(category, {}).get('folder', category.title())
            category_dir = self.base_dir / folder_name
            category_dir.mkdir(exist_ok=True)

            # Move files
            for file_path in files:
                try:
                    destination = category_dir / file_path.name

                    # Handle duplicate names
                    if destination.exists():
                        destination = self._get_unique_filename(destination)

                    shutil.move(str(file_path), str(destination))
                    moved_count += 1

                    # Log the move
                    self.organization_log.append({
                        'timestamp': datetime.now().isoformat(),
                        'action': 'move',
                        'source': str(file_path),
                        'destination': str(destination),
                        'category': category
                    })

                    print(f"📦 Moved: {file_path.name} → {folder_name}/")

                except Exception as e:
                    print(f"❌ Error moving {file_path.name}: {e}")

        return moved_count

    def _get_unique_filename(self, file_path: Path) -> Path:
        """Generate a unique filename if the original already exists"""
        base = file_path.stem
        extension = file_path.suffix
        parent = file_path.parent
        counter = 1

        while True:
            new_name = f"{base}_{counter}{extension}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1

class FileIndexer:
    """
    Creates searchable indexes of files for quick location and retrieval
    """

    def __init__(self, base_directory: Path):
        """Initialize the file indexer"""
        self.base_dir = Path(base_directory)
        self.index_file = self.base_dir / ".file_index.json"
        self.index = {}

        print(f"✅ File Indexer initialized for: {self.base_dir}")

    def create_index(self, include_content: bool = True) -> Dict[str, Any]:
        """
        Create a comprehensive index of all files

        Args:
            include_content: Whether to index file contents for text files

        Returns:
            Dictionary containing the file index
        """
        print(f"🗂️  Creating file index...")

        index = {
            'created': datetime.now().isoformat(),
            'base_directory': str(self.base_dir),
            'files': {},
            'statistics': {}
        }

        files_processed = 0
        total_size = 0

        for file_path in self.base_dir.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                try:
                    # Get file information
                    stat = file_path.stat()
                    file_info = {
                        'path': str(file_path.relative_to(self.base_dir)),
                        'absolute_path': str(file_path),
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'extension': file_path.suffix.lower(),
                        'category': FileClassifier().classify_file(file_path)
                    }

                    # Add content hash for duplicate detection
                    file_info['hash'] = self._get_file_hash(file_path)

                    # Add content preview for text files
                    if include_content and self._is_text_file(file_path):
                        content_info = self._extract_text_content(file_path)
                        file_info.update(content_info)

                    # Use relative path as key
                    key = str(file_path.relative_to(self.base_dir))
                    index['files'][key] = file_info

                    files_processed += 1
                    total_size += stat.st_size

                except Exception as e:
                    print(f"⚠️  Error indexing {file_path.name}: {e}")

        # Add statistics
        index['statistics'] = {
            'total_files': files_processed,
            'total_size': total_size,
            'categories': self._get_category_stats(index['files'])
        }

        self.index = index
        self._save_index()

        print(f"✅ Index created: {files_processed} files, {total_size / (1024*1024):.1f} MB")
        return index

    def _get_file_hash(self, file_path: Path) -> str:
        """Generate MD5 hash of file for duplicate detection"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""

    def _is_text_file(self, file_path: Path) -> bool:
        """Check if a file is likely to be a text file"""
        text_extensions = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv'}

        if file_path.suffix.lower() in text_extensions:
            return True

        # Try reading a small sample to see if it's text
        try:
            with open(file_path, 'rb') as f:
                sample = f.read(1024)

            # Check if the sample is mostly printable ASCII
            try:
                sample.decode('utf-8')
                return True
            except UnicodeDecodeError:
                return False
        except Exception:
            return False

    def _extract_text_content(self, file_path: Path) -> Dict[str, Any]:
        """Extract text content and metadata from a file"""
        content_info = {
            'preview': '',
            'word_count': 0,
            'line_count': 0,
            'keywords': []
        }

        try:
            # Detect encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read(1024)
            encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'

            # Read content
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                content = f.read()

            # Extract preview (first 500 characters)
            content_info['preview'] = content[:500].replace('\n', ' ').strip()

            # Count words and lines
            content_info['word_count'] = len(content.split())
            content_info['line_count'] = len(content.splitlines())

            # Extract keywords (most common words, excluding common stop words)
            stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}

            words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
            word_freq = Counter(word for word in words if word not in stop_words)
            content_info['keywords'] = [word for word, freq in word_freq.most_common(10)]

        except Exception as e:
            print(f"⚠️  Error extracting content from {file_path.name}: {e}")

        return content_info

    def _get_category_stats(self, files: Dict) -> Dict[str, int]:
        """Get statistics about file categories"""
        categories = defaultdict(int)
        for file_info in files.values():
            categories[file_info['category']] += 1
        return dict(categories)

    def _save_index(self):
        """Save the index to a JSON file"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
            print(f"💾 Index saved to: {self.index_file}")
        except Exception as e:
            print(f"❌ Error saving index: {e}")

    def search_files(self, query: str, search_type: str = 'all') -> List[Dict[str, Any]]:
        """
        Search for files based on various criteria

        Args:
            query: Search query
            search_type: Type of search ('name', 'content', 'category', 'all')

        Returns:
            List of matching file information
        """
        if not self.index:
            self._load_index()

        if not self.index:
            print("❌ No index available. Please create an index first.")
            return []

        query_lower = query.lower()
        results = []

        for file_path, file_info in self.index.get('files', {}).items():
            match = False

            if search_type in ['name', 'all']:
                if query_lower in file_path.lower():
                    match = True

            if search_type in ['content', 'all'] and 'preview' in file_info:
                if query_lower in file_info['preview'].lower():
                    match = True

            if search_type in ['category', 'all']:
                if query_lower in file_info.get('category', '').lower():
                    match = True

            if search_type in ['keywords', 'all'] and 'keywords' in file_info:
                if any(query_lower in keyword for keyword in file_info['keywords']):
                    match = True

            if match:
                results.append({
                    'path': file_path,
                    'relevance': self._calculate_relevance(query_lower, file_info),
                    **file_info
                })

        # Sort by relevance
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results

    def _calculate_relevance(self, query: str, file_info: Dict) -> float:
        """Calculate relevance score for search results"""
        score = 0.0

        # Filename match
        if query in file_info.get('path', '').lower():
            score += 10.0

        # Content match
        if 'preview' in file_info and query in file_info['preview'].lower():
            score += 5.0

        # Category match
        if query in file_info.get('category', '').lower():
            score += 3.0

        # Keywords match
        if 'keywords' in file_info:
            for keyword in file_info['keywords']:
                if query in keyword:
                    score += 2.0

        return score

    def _load_index(self):
        """Load the index from the JSON file"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.index = json.load(f)
                print(f"📖 Loaded index from: {self.index_file}")
            except Exception as e:
                print(f"❌ Error loading index: {e}")
                self.index = {}

class FileSummarizer:
    """
    Creates summaries/resumes of file contents
    """

    def __init__(self):
        """Initialize the file summarizer"""
        print("✅ File Summarizer initialized")

    def summarize_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Create a comprehensive summary of a file

        Args:
            file_path: Path to the file to summarize

        Returns:
            Dictionary containing file summary information
        """
        if not file_path.exists():
            return {'error': f"File not found: {file_path}"}

        print(f"📄 Summarizing file: {file_path.name}")

        summary = {
            'file_name': file_path.name,
            'file_path': str(file_path),
            'file_size': file_path.stat().st_size,
            'modified_date': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            'file_type': file_path.suffix.lower(),
            'summary_generated': datetime.now().isoformat()
        }

        # Type-specific summarization
        if self._is_text_file(file_path):
            summary.update(self._summarize_text_file(file_path))
        elif file_path.suffix.lower() == '.pdf' and HAS_PDF:
            summary.update(self._summarize_pdf_file(file_path))
        elif file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif'] and HAS_PIL:
            summary.update(self._summarize_image_file(file_path))
        else:
            summary['content_type'] = 'binary'
            summary['description'] = f"Binary file of type {file_path.suffix}"

        return summary

    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is a text file"""
        text_extensions = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv', '.log'}
        return file_path.suffix.lower() in text_extensions

    def _summarize_text_file(self, file_path: Path) -> Dict[str, Any]:
        """Summarize a text file"""
        try:
            # Detect encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read(1024)
            encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'

            # Read content
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                content = f.read()

            # Basic statistics
            lines = content.splitlines()
            words = content.split()

            summary = {
                'content_type': 'text',
                'character_count': len(content),
                'word_count': len(words),
                'line_count': len(lines),
                'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
                'encoding': encoding
            }

            # Extract structure for code files
            if file_path.suffix.lower() in ['.py', '.js', '.java', '.cpp', '.c']:
                summary.update(self._analyze_code_structure(content, file_path.suffix))

            # Extract first few lines as preview
            summary['preview'] = '\n'.join(lines[:10])

            # Find important sections
            summary['sections'] = self._extract_sections(content)

            return summary

        except Exception as e:
            return {'content_type': 'text', 'error': str(e)}

    def _analyze_code_structure(self, content: str, extension: str) -> Dict[str, Any]:
        """Analyze code file structure"""
        structure = {
            'functions': [],
            'classes': [],
            'imports': [],
            'comments_ratio': 0.0
        }

        lines = content.splitlines()
        comment_lines = 0

        for line in lines:
            line_stripped = line.strip()

            # Count comments
            if extension == '.py' and (line_stripped.startswith('#') or '"""' in line_stripped):
                comment_lines += 1
            elif extension in ['.js', '.java', '.cpp', '.c'] and (line_stripped.startswith('//') or '/*' in line_stripped):
                comment_lines += 1

            # Find functions
            if extension == '.py':
                if re.match(r'^\s*def\s+(\w+)', line):
                    func_match = re.search(r'def\s+(\w+)', line)
                    if func_match:
                        structure['functions'].append(func_match.group(1))
                elif re.match(r'^\s*class\s+(\w+)', line):
                    class_match = re.search(r'class\s+(\w+)', line)
                    if class_match:
                        structure['classes'].append(class_match.group(1))
                elif re.match(r'^\s*(import|from)\s+', line):
                    structure['imports'].append(line.strip())

        structure['comments_ratio'] = comment_lines / len(lines) if lines else 0
        return structure

    def _extract_sections(self, content: str) -> List[str]:
        """Extract section headers from text content"""
        sections = []
        lines = content.splitlines()

        for line in lines:
            line_stripped = line.strip()

            # Markdown headers
            if line_stripped.startswith('#'):
                sections.append(line_stripped)

            # Lines in ALL CAPS (potential headers)
            elif len(line_stripped) > 3 and line_stripped.isupper() and line_stripped.replace(' ', '').isalpha():
                sections.append(line_stripped)

        return sections[:10]  # Return first 10 sections

    def _summarize_pdf_file(self, file_path: Path) -> Dict[str, Any]:
        """Summarize a PDF file"""
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)

                summary = {
                    'content_type': 'pdf',
                    'page_count': len(pdf_reader.pages),
                    'title': pdf_reader.metadata.get('/Title', 'Unknown') if pdf_reader.metadata else 'Unknown',
                    'author': pdf_reader.metadata.get('/Author', 'Unknown') if pdf_reader.metadata else 'Unknown',
                }

                # Extract text from first few pages
                text_preview = ""
                for i, page in enumerate(pdf_reader.pages[:3]):  # First 3 pages
                    text_preview += page.extract_text() + "\n"

                summary['preview'] = text_preview[:1000]  # First 1000 characters
                summary['word_count'] = len(text_preview.split())

                return summary

        except Exception as e:
            return {'content_type': 'pdf', 'error': str(e)}

    def _summarize_image_file(self, file_path: Path) -> Dict[str, Any]:
        """Summarize an image file"""
        try:
            with Image.open(file_path) as img:
                summary = {
                    'content_type': 'image',
                    'dimensions': f"{img.width}x{img.height}",
                    'mode': img.mode,
                    'format': img.format,
                    'has_transparency': 'transparency' in img.info or img.mode in ['RGBA', 'LA']
                }

                # Basic color analysis
                if img.mode == 'RGB':
                    colors = img.getcolors(maxcolors=256*256*256)
                    if colors:
                        dominant_color = max(colors, key=lambda x: x[0])[1]
                        summary['dominant_color'] = f"RGB{dominant_color}"

                return summary

        except Exception as e:
            return {'content_type': 'image', 'error': str(e)}

class FileComparator:
    """
    Compares multiple files side by side with difference highlighting
    """

    def __init__(self):
        """Initialize the file comparator"""
        print("✅ File Comparator initialized")

    def compare_files(self, file_paths: List[Path], comparison_type: str = 'auto') -> Dict[str, Any]:
        """
        Compare multiple files and highlight differences

        Args:
            file_paths: List of file paths to compare
            comparison_type: Type of comparison ('text', 'binary', 'auto')

        Returns:
            Dictionary containing comparison results
        """
        if len(file_paths) < 2:
            return {'error': 'At least 2 files required for comparison'}

        print(f"🔍 Comparing {len(file_paths)} files...")

        # Validate all files exist
        for file_path in file_paths:
            if not file_path.exists():
                return {'error': f'File not found: {file_path}'}

        comparison = {
            'files': [str(path) for path in file_paths],
            'comparison_date': datetime.now().isoformat(),
            'file_info': []
        }

        # Get basic info for each file
        for file_path in file_paths:
            stat = file_path.stat()
            comparison['file_info'].append({
                'name': file_path.name,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'hash': self._get_file_hash(file_path)
            })

        # Determine comparison type
        if comparison_type == 'auto':
            comparison_type = 'text' if all(self._is_text_file(path) for path in file_paths) else 'binary'

        # Perform comparison
        if comparison_type == 'text':
            comparison.update(self._compare_text_files(file_paths))
        else:
            comparison.update(self._compare_binary_files(file_paths))

        return comparison

    def _compare_text_files(self, file_paths: List[Path]) -> Dict[str, Any]:
        """Compare text files line by line"""
        try:
            # Read all files
            file_contents = []
            for file_path in file_paths:
                # Detect encoding
                with open(file_path, 'rb') as f:
                    raw_data = f.read(1024)
                encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'

                # Read content
                with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                    file_contents.append(content.splitlines())

            # Calculate similarity
            similarity_matrix = self._calculate_text_similarity_matrix(file_contents)

            # Generate unified diff for first two files
            if len(file_contents) >= 2:
                diff = list(difflib.unified_diff(
                    file_contents[0],
                    file_contents[1],
                    fromfile=file_paths[0].name,
                    tofile=file_paths[1].name,
                    lineterm=''
                ))
            else:
                diff = []

            return {
                'comparison_type': 'text',
                'similarity_matrix': similarity_matrix,
                'unified_diff': diff[:100],  # Limit diff output
                'statistics': self._get_text_comparison_stats(file_contents)
            }

        except Exception as e:
            return {'comparison_type': 'text', 'error': str(e)}

    def _compare_binary_files(self, file_paths: List[Path]) -> Dict[str, Any]:
        """Compare binary files by hash and size"""
        try:
            hashes = [self._get_file_hash(path) for path in file_paths]
            sizes = [path.stat().st_size for path in file_paths]

            # Check for identical files
            identical_groups = defaultdict(list)
            for i, hash_val in enumerate(hashes):
                identical_groups[hash_val].append(i)

            identical_files = [group for group in identical_groups.values() if len(group) > 1]

            return {
                'comparison_type': 'binary',
                'hashes': hashes,
                'sizes': sizes,
                'identical_files': identical_files,
                'all_identical': len(set(hashes)) == 1
            }

        except Exception as e:
            return {'comparison_type': 'binary', 'error': str(e)}

    def _calculate_text_similarity_matrix(self, file_contents: List[List[str]]) -> List[List[float]]:
        """Calculate similarity matrix for text files"""
        n = len(file_contents)
        matrix = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i == j:
                    matrix[i][j] = 1.0
                else:
                    # Calculate similarity ratio
                    text1 = '\n'.join(file_contents[i])
                    text2 = '\n'.join(file_contents[j])

                    # Use textdistance if available, otherwise use difflib
                    if HAS_TEXTDISTANCE:
                        similarity = textdistance.jaro_winkler(text1, text2)
                    else:
                        similarity = difflib.SequenceMatcher(None, text1, text2).ratio()

                    matrix[i][j] = similarity

        return matrix

    def _get_text_comparison_stats(self, file_contents: List[List[str]]) -> Dict[str, Any]:
        """Get statistical comparison of text files"""
        stats = {
            'line_counts': [len(content) for content in file_contents],
            'word_counts': [],
            'character_counts': []
        }

        for content_lines in file_contents:
            content_text = '\n'.join(content_lines)
            stats['word_counts'].append(len(content_text.split()))
            stats['character_counts'].append(len(content_text))

        return stats

    def _get_file_hash(self, file_path: Path) -> str:
        """Generate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""

    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is a text file"""
        text_extensions = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv', '.log'}

        if file_path.suffix.lower() in text_extensions:
            return True

        try:
            with open(file_path, 'rb') as f:
                sample = f.read(1024)
            sample.decode('utf-8')
            return True
        except (UnicodeDecodeError, Exception):
            return False

def create_sample_files(sample_dir: Path):
    """Create sample files for demonstration"""
    sample_dir.mkdir(exist_ok=True)

    # Create various sample files
    files_to_create = {
        'report.txt': """# Annual Report 2024

## Executive Summary
This document provides an overview of our company's performance in 2024.

## Financial Highlights
- Revenue: $10M
- Profit: $2M
- Growth: 15%

## Future Plans
We plan to expand our operations in the coming year.
""",
        'script.py': """#!/usr/bin/env python3
\"\"\"
Sample Python script for demonstration
\"\"\"

def hello_world():
    \"\"\"Print hello world message\"\"\"
    print("Hello, World!")

def calculate_sum(a, b):
    \"\"\"Calculate sum of two numbers\"\"\"
    return a + b

if __name__ == "__main__":
    hello_world()
    result = calculate_sum(5, 3)
    print(f"Sum: {result}")
""",
        'data.csv': """Name,Age,City
Alice,30,New York
Bob,25,San Francisco
Charlie,35,Chicago
Diana,28,Boston
""",
        'notes.md': """# Meeting Notes

## Date: March 15, 2024

### Attendees
- Alice Johnson
- Bob Smith
- Charlie Brown

### Action Items
1. Complete budget review
2. Update project timeline
3. Schedule follow-up meeting

### Next Steps
Review progress next week.
""",
        'similar_script.py': """#!/usr/bin/env python3
\"\"\"
Another Python script for comparison
\"\"\"

def greet():
    \"\"\"Print greeting message\"\"\"
    print("Hello, Python!")

def add_numbers(x, y):
    \"\"\"Add two numbers\"\"\"
    return x + y

if __name__ == "__main__":
    greet()
    total = add_numbers(10, 5)
    print(f"Total: {total}")
""",
    }

    for filename, content in files_to_create.items():
        file_path = sample_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    print(f"✅ Created {len(files_to_create)} sample files in {sample_dir}")

def main():
    """
    Main function demonstrating the file organizer functionality
    """
    print("📁 LA File Organizer - Educational Demo")
    print("=" * 50)

    # Set up demo directory
    demo_dir = Path(__file__).parent / "file_organizer_demo"
    sample_dir = demo_dir / "sample_files"

    # Create sample files
    print("\n📚 Example 1: Creating sample files...")
    create_sample_files(sample_dir)

    # Initialize components
    organizer = FileOrganizer(demo_dir)
    indexer = FileIndexer(demo_dir)
    summarizer = FileSummarizer()
    comparator = FileComparator()

    # Example 1: Organize files (dry run first)
    print("\n📚 Example 2: File organization (dry run)...")
    organization_results = organizer.organize_files(sample_dir, dry_run=True)

    print(f"Organization plan:")
    for category, files in organization_results['categories'].items():
        print(f"  {category}: {len(files)} files")

    # Example 2: Create file index
    print("\n📚 Example 3: Creating file index...")
    index_results = indexer.create_index(include_content=True)

    print(f"Index statistics:")
    for category, count in index_results['statistics']['categories'].items():
        print(f"  {category}: {count} files")

    # Example 3: Search files
    print("\n📚 Example 4: Searching files...")
    search_results = indexer.search_files("python", search_type='all')

    print(f"Search results for 'python':")
    for result in search_results[:3]:  # Show top 3 results
        print(f"  {result['path']} (relevance: {result['relevance']:.1f})")

    # Example 4: Summarize a file
    print("\n📚 Example 5: File summarization...")
    script_file = sample_dir / "script.py"
    if script_file.exists():
        summary = summarizer.summarize_file(script_file)
        print(f"Summary of {script_file.name}:")
        print(f"  Type: {summary.get('content_type', 'unknown')}")
        print(f"  Lines: {summary.get('line_count', 0)}")
        print(f"  Words: {summary.get('word_count', 0)}")
        if 'functions' in summary:
            print(f"  Functions: {', '.join(summary['functions'])}")

    # Example 5: Compare files
    print("\n📚 Example 6: File comparison...")
    script1 = sample_dir / "script.py"
    script2 = sample_dir / "similar_script.py"

    if script1.exists() and script2.exists():
        comparison = comparator.compare_files([script1, script2])

        if 'similarity_matrix' in comparison:
            similarity = comparison['similarity_matrix'][0][1]
            print(f"Similarity between scripts: {similarity:.2%}")

        if 'unified_diff' in comparison and comparison['unified_diff']:
            print("First few differences:")
            for line in comparison['unified_diff'][:10]:
                print(f"  {line}")

    # Example 6: Find duplicate files
    print("\n📚 Example 7: Finding duplicate files...")
    all_files = list(sample_dir.rglob('*'))
    file_hashes = {}

    for file_path in all_files:
        if file_path.is_file():
            file_hash = comparator._get_file_hash(file_path)
            if file_hash in file_hashes:
                print(f"Potential duplicate found:")
                print(f"  Original: {file_hashes[file_hash]}")
                print(f"  Duplicate: {file_path}")
            else:
                file_hashes[file_hash] = file_path

    print(f"\n🎓 Educational Notes:")
    print("1. Always backup files before reorganizing")
    print("2. Use dry runs to test organization logic")
    print("3. Index files periodically to keep search current")
    print("4. Handle different file encodings carefully")
    print("5. Consider memory usage when processing large files")
    print("6. Use appropriate similarity algorithms for your use case")
    print("7. Regular maintenance keeps file systems organized")

    # Cleanup
    try:
        shutil.rmtree(demo_dir)
        print(f"🧹 Cleaned up demo directory: {demo_dir}")
    except Exception as e:
        print(f"⚠️  Could not clean up demo directory: {e}")

if __name__ == "__main__":
    main()