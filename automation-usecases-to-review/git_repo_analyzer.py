#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "rich>=13.0.0",
#     "gitpython>=3.1.0",
# ]
# ///
"""
Git Repo Analyzer - Analyze git repositories and generate insights
Usage: python git_repo_analyzer.py [repository_path]
"""

import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
import git

console = Console()


class GitRepoAnalyzer:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        try:
            self.repo = git.Repo(repo_path)
        except git.InvalidGitRepositoryError:
            console.print(f"[red]Error: '{repo_path}' is not a valid git repository[/red]")
            raise

    def get_basic_info(self) -> Dict:
        """Get basic repository information."""
        try:
            active_branch = self.repo.active_branch.name
        except:
            active_branch = "HEAD detached"

        return {
            'path': str(self.repo_path),
            'active_branch': active_branch,
            'total_branches': len(list(self.repo.branches)),
            'total_tags': len(list(self.repo.tags)),
            'is_bare': self.repo.bare,
            'has_remote': len(list(self.repo.remotes)) > 0,
            'remotes': [remote.name for remote in self.repo.remotes]
        }

    def get_commit_stats(self, since_days: int = 30) -> Dict:
        """Analyze commit statistics."""
        since_date = datetime.now() - timedelta(days=since_days)

        commits = list(self.repo.iter_commits(max_count=1000))
        recent_commits = [c for c in commits if datetime.fromtimestamp(c.committed_date) > since_date]

        # Author statistics
        author_commits = Counter(c.author.name for c in commits)
        recent_author_commits = Counter(c.author.name for c in recent_commits)

        # Time statistics
        commit_by_day = Counter(
            datetime.fromtimestamp(c.committed_date).strftime('%A')
            for c in commits
        )

        commit_by_hour = Counter(
            datetime.fromtimestamp(c.committed_date).hour
            for c in commits
        )

        # Calculate average commit message length
        avg_msg_length = sum(len(c.message) for c in commits) / len(commits) if commits else 0

        return {
            'total_commits': len(commits),
            'recent_commits': len(recent_commits),
            'total_authors': len(author_commits),
            'top_authors': author_commits.most_common(10),
            'recent_top_authors': recent_author_commits.most_common(5),
            'commits_by_day': commit_by_day,
            'commits_by_hour': commit_by_hour,
            'avg_message_length': avg_msg_length,
            'last_commit_date': datetime.fromtimestamp(commits[0].committed_date) if commits else None
        }

    def get_file_stats(self) -> Dict:
        """Analyze file statistics in the repository."""
        file_extensions = Counter()
        file_sizes = defaultdict(int)
        total_lines = 0
        total_files = 0

        # Common code extensions to analyze
        code_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.rb',
            '.php', '.swift', '.kt', '.scala', '.sh', '.bash', '.html', '.css',
            '.jsx', '.tsx', '.vue', '.sql', '.r', '.m', '.h'
        }

        for root, dirs, files in os.walk(self.repo_path):
            # Skip .git directory
            if '.git' in root:
                continue

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = Path(root) / file
                extension = file_path.suffix.lower()

                file_extensions[extension] += 1
                total_files += 1

                try:
                    file_size = file_path.stat().st_size
                    file_sizes[extension] += file_size

                    # Count lines for code files
                    if extension in code_extensions and file_size < 1_000_000:  # Skip huge files
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                total_lines += sum(1 for line in f)
                        except:
                            pass
                except:
                    pass

        return {
            'total_files': total_files,
            'file_extensions': file_extensions.most_common(15),
            'largest_extensions': sorted(
                [(ext, size) for ext, size in file_sizes.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10],
            'total_lines': total_lines
        }

    def get_branch_info(self) -> List[Dict]:
        """Get information about all branches."""
        branches = []

        for branch in self.repo.branches:
            try:
                commit = branch.commit
                branches.append({
                    'name': branch.name,
                    'last_commit': datetime.fromtimestamp(commit.committed_date),
                    'author': commit.author.name,
                    'message': commit.message.split('\n')[0][:50]
                })
            except:
                pass

        return sorted(branches, key=lambda x: x['last_commit'], reverse=True)

    def get_large_files(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Find largest files in the repository."""
        files = []

        for root, dirs, filenames in os.walk(self.repo_path):
            if '.git' in root:
                continue

            for filename in filenames:
                if filename.startswith('.'):
                    continue

                file_path = Path(root) / filename
                try:
                    size = file_path.stat().st_size
                    rel_path = file_path.relative_to(self.repo_path)
                    files.append((str(rel_path), size))
                except:
                    pass

        return sorted(files, key=lambda x: x[1], reverse=True)[:limit]

    def get_commit_frequency(self, days: int = 30) -> Dict[str, int]:
        """Get commit frequency over the last N days."""
        since_date = datetime.now() - timedelta(days=days)
        commits = list(self.repo.iter_commits(max_count=1000))

        frequency = defaultdict(int)
        for commit in commits:
            commit_date = datetime.fromtimestamp(commit.committed_date)
            if commit_date > since_date:
                date_str = commit_date.strftime('%Y-%m-%d')
                frequency[date_str] += 1

        return dict(frequency)


def get_size_str(size_bytes: int) -> str:
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def display_analysis(analyzer: GitRepoAnalyzer, since_days: int = 30):
    """Display comprehensive repository analysis."""

    console.print("\n[bold cyan]Git Repository Analysis[/bold cyan]\n")

    # Basic Info
    basic_info = analyzer.get_basic_info()
    info_panel = Panel(
        f"[bold]Path:[/bold] {basic_info['path']}\n"
        f"[bold]Active Branch:[/bold] {basic_info['active_branch']}\n"
        f"[bold]Branches:[/bold] {basic_info['total_branches']}\n"
        f"[bold]Tags:[/bold] {basic_info['total_tags']}\n"
        f"[bold]Remotes:[/bold] {', '.join(basic_info['remotes']) if basic_info['remotes'] else 'None'}",
        title="Repository Info",
        border_style="cyan"
    )
    console.print(info_panel)
    console.print()

    # Commit Statistics
    console.print("[bold yellow]Analyzing commits...[/bold yellow]")
    commit_stats = analyzer.get_commit_stats(since_days)

    table = Table(title=f"Commit Statistics (Last {since_days} days)", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green", justify="right")

    table.add_row("Total Commits (all time)", str(commit_stats['total_commits']))
    table.add_row(f"Recent Commits ({since_days} days)", str(commit_stats['recent_commits']))
    table.add_row("Total Authors", str(commit_stats['total_authors']))
    table.add_row("Avg Message Length", f"{commit_stats['avg_message_length']:.0f} chars")

    if commit_stats['last_commit_date']:
        table.add_row("Last Commit", commit_stats['last_commit_date'].strftime('%Y-%m-%d %H:%M'))

    console.print(table)
    console.print()

    # Top Authors
    if commit_stats['top_authors']:
        table = Table(title="Top Contributors (All Time)", show_header=True)
        table.add_column("Author", style="cyan")
        table.add_column("Commits", style="green", justify="right")
        table.add_column("Percentage", style="yellow", justify="right")

        total = commit_stats['total_commits']
        for author, count in commit_stats['top_authors'][:10]:
            percentage = (count / total * 100) if total > 0 else 0
            table.add_row(author, str(count), f"{percentage:.1f}%")

        console.print(table)
        console.print()

    # File Statistics
    console.print("[bold yellow]Analyzing files...[/bold yellow]")
    file_stats = analyzer.get_file_stats()

    table = Table(title="File Statistics", show_header=True)
    table.add_column("Extension", style="cyan")
    table.add_column("Files", style="green", justify="right")
    table.add_column("Total Size", style="yellow", justify="right")

    for (ext, count), (_, size) in zip(
        file_stats['file_extensions'][:10],
        file_stats['largest_extensions'][:10]
    ):
        table.add_row(
            ext if ext else "(no extension)",
            str(count),
            get_size_str(size)
        )

    console.print(table)
    console.print(f"\n[bold]Total Files:[/bold] {file_stats['total_files']}")
    console.print(f"[bold]Total Lines of Code:[/bold] {file_stats['total_lines']:,}")
    console.print()

    # Largest Files
    console.print("[bold yellow]Finding largest files...[/bold yellow]")
    large_files = analyzer.get_large_files(10)

    table = Table(title="Largest Files", show_header=True)
    table.add_column("File", style="cyan", max_width=60)
    table.add_column("Size", style="yellow", justify="right")

    for file_path, size in large_files:
        table.add_row(file_path, get_size_str(size))

    console.print(table)
    console.print()

    # Branch Information
    branches = analyzer.get_branch_info()
    if branches:
        table = Table(title="Branches", show_header=True)
        table.add_column("Branch", style="cyan")
        table.add_column("Last Commit", style="yellow")
        table.add_column("Author", style="green")

        for branch in branches[:10]:
            table.add_row(
                branch['name'],
                branch['last_commit'].strftime('%Y-%m-%d %H:%M'),
                branch['author']
            )

        console.print(table)
        console.print()

    # Commit Activity Pattern
    console.print("[bold cyan]Commit Activity Patterns[/bold cyan]\n")

    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    table = Table(title="Commits by Day of Week")
    table.add_column("Day", style="cyan")
    table.add_column("Commits", style="green", justify="right")
    table.add_column("Bar", style="yellow")

    max_commits = max(commit_stats['commits_by_day'].values()) if commit_stats['commits_by_day'] else 1

    for day in day_order:
        count = commit_stats['commits_by_day'].get(day, 0)
        bar_length = int((count / max_commits) * 30) if max_commits > 0 else 0
        bar = '█' * bar_length
        table.add_row(day, str(count), bar)

    console.print(table)


def main():
    parser = argparse.ArgumentParser(
        description="Git Repository Analyzer - Analyze git repositories"
    )
    parser.add_argument(
        "repository",
        nargs="?",
        default=".",
        help="Path to git repository (default: current directory)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days for recent activity analysis (default: 30)"
    )
    parser.add_argument(
        "--export",
        type=str,
        help="Export analysis to JSON file"
    )

    args = parser.parse_args()

    repo_path = Path(args.repository).resolve()

    if not repo_path.exists():
        console.print(f"[red]Error: Path '{repo_path}' does not exist[/red]")
        return

    try:
        analyzer = GitRepoAnalyzer(repo_path)
        display_analysis(analyzer, args.days)

        if args.export:
            import json
            export_data = {
                'basic_info': analyzer.get_basic_info(),
                'commit_stats': analyzer.get_commit_stats(args.days),
                'file_stats': analyzer.get_file_stats(),
                'branches': analyzer.get_branch_info(),
                'large_files': analyzer.get_large_files(),
                'commit_frequency': analyzer.get_commit_frequency(args.days)
            }

            # Convert datetime objects to strings for JSON serialization
            def convert_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return obj

            with open(args.export, 'w') as f:
                json.dump(export_data, f, indent=2, default=convert_datetime)

            console.print(f"\n[green]Analysis exported to: {args.export}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    main()
