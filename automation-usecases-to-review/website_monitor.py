#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests>=2.31.0",
#     "beautifulsoup4>=4.12.0",
#     "rich>=13.0.0",
# ]
# ///
"""
Website Monitor - Track changes on websites and get notified
Usage: python website_monitor.py --url https://example.com --selector ".price" --interval 60
"""

import hashlib
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import argparse
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel

console = Console()


class WebsiteMonitor:
    def __init__(self, config_file: Path = Path("monitor_config.json")):
        self.config_file = config_file
        self.sites = []
        self.history_file = Path("monitor_history.json")
        self.load_config()
        self.load_history()

    def load_config(self):
        """Load monitoring configuration from file."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                self.sites = data.get('sites', [])
        else:
            self.sites = []

    def save_config(self):
        """Save monitoring configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump({'sites': self.sites}, f, indent=2)

    def load_history(self):
        """Load monitoring history from file."""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                self.history = json.load(f)
        else:
            self.history = {}

    def save_history(self):
        """Save monitoring history to file."""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)

    def add_site(self, name: str, url: str, selector: Optional[str] = None,
                 interval: int = 300, notify: bool = True):
        """Add a new site to monitor."""
        site = {
            'name': name,
            'url': url,
            'selector': selector,
            'interval': interval,
            'notify': notify,
            'added': datetime.now().isoformat(),
            'last_check': None,
            'last_hash': None,
            'status': 'active'
        }
        self.sites.append(site)
        self.save_config()
        console.print(f"[green]Added site: {name}[/green]")

    def remove_site(self, name: str):
        """Remove a site from monitoring."""
        self.sites = [s for s in self.sites if s['name'] != name]
        self.save_config()
        console.print(f"[yellow]Removed site: {name}[/yellow]")

    def fetch_content(self, url: str, selector: Optional[str] = None) -> Optional[str]:
        """Fetch content from URL, optionally extracting specific element."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            if selector:
                soup = BeautifulSoup(response.content, 'html.parser')
                element = soup.select_one(selector)
                if element:
                    return element.get_text(strip=True)
                else:
                    console.print(f"[yellow]Selector '{selector}' not found[/yellow]")
                    return None
            else:
                return response.text

        except requests.RequestException as e:
            console.print(f"[red]Error fetching {url}: {e}[/red]")
            return None

    def calculate_hash(self, content: str) -> str:
        """Calculate hash of content."""
        return hashlib.sha256(content.encode()).hexdigest()

    def check_site(self, site: Dict) -> Dict:
        """Check a single site for changes."""
        name = site['name']
        url = site['url']
        selector = site.get('selector')

        console.print(f"[cyan]Checking {name}...[/cyan]")

        content = self.fetch_content(url, selector)

        if content is None:
            return {
                'name': name,
                'status': 'error',
                'changed': False,
                'timestamp': datetime.now().isoformat()
            }

        current_hash = self.calculate_hash(content)
        last_hash = site.get('last_hash')

        changed = last_hash is not None and current_hash != last_hash

        # Update site info
        site['last_check'] = datetime.now().isoformat()
        site['last_hash'] = current_hash

        # Save to history
        if name not in self.history:
            self.history[name] = []

        self.history[name].append({
            'timestamp': datetime.now().isoformat(),
            'hash': current_hash,
            'changed': changed,
            'content_preview': content[:200] if len(content) > 200 else content
        })

        # Keep only last 100 entries per site
        self.history[name] = self.history[name][-100:]

        self.save_config()
        self.save_history()

        return {
            'name': name,
            'url': url,
            'status': 'success',
            'changed': changed,
            'timestamp': datetime.now().isoformat(),
            'content_preview': content[:200] if len(content) > 200 else content
        }

    def check_all(self) -> List[Dict]:
        """Check all monitored sites."""
        results = []
        for site in self.sites:
            if site.get('status') == 'active':
                result = self.check_site(site)
                results.append(result)
                time.sleep(1)  # Be nice to servers
        return results

    def monitor_loop(self, interval: int = 300):
        """Continuously monitor sites at specified interval."""
        console.print(f"\n[bold cyan]Starting continuous monitoring (interval: {interval}s)[/bold cyan]")
        console.print("[yellow]Press Ctrl+C to stop[/yellow]\n")

        try:
            while True:
                results = self.check_all()

                # Display results
                table = Table(title=f"Monitor Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                table.add_column("Site", style="cyan")
                table.add_column("Status", style="white")
                table.add_column("Changed", style="white")
                table.add_column("Preview", style="white", max_width=50)

                for result in results:
                    status_style = "green" if result['status'] == 'success' else "red"
                    changed_style = "yellow bold" if result.get('changed') else "white"

                    table.add_row(
                        result['name'],
                        f"[{status_style}]{result['status'].upper()}[/{status_style}]",
                        f"[{changed_style}]{'YES' if result.get('changed') else 'NO'}[/{changed_style}]",
                        result.get('content_preview', 'N/A')[:50]
                    )

                console.clear()
                console.print(table)

                # Alert on changes
                for result in results:
                    if result.get('changed'):
                        console.print(f"\n[bold yellow]CHANGE DETECTED: {result['name']}[/bold yellow]")
                        console.print(f"URL: {result['url']}")
                        console.print(f"Preview: {result.get('content_preview', 'N/A')[:100]}\n")

                console.print(f"\n[dim]Next check in {interval} seconds...[/dim]")
                time.sleep(interval)

        except KeyboardInterrupt:
            console.print("\n[yellow]Monitoring stopped[/yellow]")

    def show_history(self, site_name: Optional[str] = None, limit: int = 10):
        """Show monitoring history."""
        if site_name:
            if site_name in self.history:
                history = self.history[site_name][-limit:]
                table = Table(title=f"History for {site_name}")
                table.add_column("Timestamp", style="cyan")
                table.add_column("Changed", style="white")
                table.add_column("Preview", style="white", max_width=50)

                for entry in history:
                    changed_style = "yellow" if entry.get('changed') else "white"
                    table.add_row(
                        entry['timestamp'][:19],
                        f"[{changed_style}]{'YES' if entry.get('changed') else 'NO'}[/{changed_style}]",
                        entry.get('content_preview', 'N/A')[:50]
                    )

                console.print(table)
            else:
                console.print(f"[yellow]No history found for {site_name}[/yellow]")
        else:
            # Show summary for all sites
            table = Table(title="Monitoring History Summary")
            table.add_column("Site", style="cyan")
            table.add_column("Checks", style="white", justify="right")
            table.add_column("Changes", style="yellow", justify="right")
            table.add_column("Last Check", style="white")

            for site_name, entries in self.history.items():
                changes = sum(1 for e in entries if e.get('changed'))
                last_check = entries[-1]['timestamp'][:19] if entries else "Never"

                table.add_row(
                    site_name,
                    str(len(entries)),
                    str(changes),
                    last_check
                )

            console.print(table)

    def list_sites(self):
        """List all monitored sites."""
        if not self.sites:
            console.print("[yellow]No sites configured[/yellow]")
            return

        table = Table(title="Monitored Sites")
        table.add_column("Name", style="cyan")
        table.add_column("URL", style="white")
        table.add_column("Selector", style="yellow")
        table.add_column("Interval", style="green", justify="right")
        table.add_column("Status", style="white")

        for site in self.sites:
            table.add_row(
                site['name'],
                site['url'][:50],
                site.get('selector', 'N/A')[:30],
                f"{site.get('interval', 300)}s",
                site.get('status', 'active')
            )

        console.print(table)


def main():
    parser = argparse.ArgumentParser(
        description="Website Monitor - Track changes on websites"
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Add site command
    add_parser = subparsers.add_parser('add', help='Add a site to monitor')
    add_parser.add_argument('--name', required=True, help='Site name')
    add_parser.add_argument('--url', required=True, help='URL to monitor')
    add_parser.add_argument('--selector', help='CSS selector for specific element')
    add_parser.add_argument('--interval', type=int, default=300, help='Check interval in seconds')

    # Remove site command
    remove_parser = subparsers.add_parser('remove', help='Remove a site')
    remove_parser.add_argument('name', help='Site name to remove')

    # List sites command
    subparsers.add_parser('list', help='List all monitored sites')

    # Check command
    check_parser = subparsers.add_parser('check', help='Check sites once')
    check_parser.add_argument('--name', help='Specific site name to check')

    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Start continuous monitoring')
    monitor_parser.add_argument('--interval', type=int, default=300, help='Check interval in seconds')

    # History command
    history_parser = subparsers.add_parser('history', help='Show monitoring history')
    history_parser.add_argument('--name', help='Specific site name')
    history_parser.add_argument('--limit', type=int, default=10, help='Number of entries to show')

    args = parser.parse_args()

    monitor = WebsiteMonitor()

    if args.command == 'add':
        monitor.add_site(args.name, args.url, args.selector, args.interval)

    elif args.command == 'remove':
        monitor.remove_site(args.name)

    elif args.command == 'list':
        monitor.list_sites()

    elif args.command == 'check':
        if args.name:
            site = next((s for s in monitor.sites if s['name'] == args.name), None)
            if site:
                result = monitor.check_site(site)
                console.print(f"\n[bold]Result:[/bold]")
                console.print(f"Status: {result['status']}")
                console.print(f"Changed: {result.get('changed', False)}")
                console.print(f"Preview: {result.get('content_preview', 'N/A')[:200]}")
            else:
                console.print(f"[red]Site '{args.name}' not found[/red]")
        else:
            results = monitor.check_all()
            console.print(f"\n[green]Checked {len(results)} sites[/green]")

    elif args.command == 'monitor':
        monitor.monitor_loop(args.interval)

    elif args.command == 'history':
        monitor.show_history(args.name, args.limit)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
