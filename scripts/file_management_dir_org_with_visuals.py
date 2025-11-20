#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "pandas>=2.0.0",
#     "matplotlib>=3.7.0",
#     "seaborn>=0.12.0",
#     "plotly>=5.17.0",
#     "rich>=13.0.0",
#     "numpy>=1.24.0"
# ]
# ///

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
import sys
import numpy as np

def get_file_size_mb(size_bytes):
    """Convert bytes to MB"""
    return round(size_bytes / (1024 * 1024), 2)

def get_file_info(root_path):
    """Scan all files in the directory tree and collect information"""
    files_data = []
    console = Console()
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Scanning files...", total=None)
        
        for root, dirs, files in os.walk(root_path):
            for file in files:
                # Skip hidden files and system files
                if file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                try:
                    stat_info = os.stat(file_path)
                    
                    # Get relative folder path
                    rel_folder = os.path.relpath(root, root_path)
                    if rel_folder == '.':
                        rel_folder = 'Root'
                    
                    # Get file extension
                    ext = os.path.splitext(file)[1].lower()
                    if not ext:
                        ext = 'No Extension'
                    
                    # File size in MB
                    size_mb = get_file_size_mb(stat_info.st_size)
                    
                    # Last modified date
                    mod_time = datetime.fromtimestamp(stat_info.st_mtime)
                    
                    files_data.append({
                        'filename': file,
                        'folder': rel_folder,
                        'extension': ext,
                        'size_mb': size_mb,
                        'size_bytes': stat_info.st_size,
                        'modified_date': mod_time,
                        'full_path': file_path
                    })
                    
                    progress.advance(task)
                    
                except (OSError, IOError):
                    # Skip files that can't be accessed
                    continue
    
    return pd.DataFrame(files_data)

def create_summary_table(df):
    """Create a rich summary table"""
    console = Console()
    
    # Overall summary
    table = Table(title="📁 Folder Summary", style="cyan")
    table.add_column("Metric", style="bold blue")
    table.add_column("Value", style="green")
    
    total_files = len(df)
    total_size_gb = df['size_mb'].sum() / 1024
    avg_file_size = df['size_mb'].mean()
    largest_file = df.loc[df['size_mb'].idxmax()]
    
    table.add_row("Total Files", f"{total_files:,}")
    table.add_row("Total Size", f"{total_size_gb:.2f} GB")
    table.add_row("Average File Size", f"{avg_file_size:.2f} MB")
    table.add_row("Largest File", f"{largest_file['filename']} ({largest_file['size_mb']:.2f} MB)")
    table.add_row("Total Folders", f"{df['folder'].nunique()}")
    table.add_row("File Types", f"{df['extension'].nunique()}")
    
    console.print(table)
    console.print()

def create_folder_breakdown_table(df):
    """Create a breakdown by folder"""
    console = Console()
    
    folder_summary = df.groupby('folder').agg({
        'filename': 'count',
        'size_mb': ['sum', 'mean'],
        'extension': 'nunique'
    }).round(2)
    
    folder_summary.columns = ['File Count', 'Total Size (MB)', 'Avg Size (MB)', 'File Types']
    folder_summary = folder_summary.sort_values('Total Size (MB)', ascending=False)
    
    table = Table(title="📂 Breakdown by Folder", style="yellow")
    table.add_column("Folder", style="bold cyan")
    table.add_column("Files", justify="right", style="green")
    table.add_column("Total Size (MB)", justify="right", style="blue")
    table.add_column("Avg Size (MB)", justify="right", style="magenta")
    table.add_column("File Types", justify="right", style="yellow")
    
    for folder, row in folder_summary.head(20).iterrows():
        table.add_row(
            folder,
            f"{int(row['File Count']):,}",
            f"{row['Total Size (MB)']:,.2f}",
            f"{row['Avg Size (MB)']:,.2f}",
            f"{int(row['File Types'])}"
        )
    
    console.print(table)
    console.print()

def create_file_type_table(df):
    """Create a breakdown by file type"""
    console = Console()
    
    ext_summary = df.groupby('extension').agg({
        'filename': 'count',
        'size_mb': ['sum', 'mean']
    }).round(2)
    
    ext_summary.columns = ['File Count', 'Total Size (MB)', 'Avg Size (MB)']
    ext_summary = ext_summary.sort_values('File Count', ascending=False)
    
    table = Table(title="📄 Breakdown by File Type", style="green")
    table.add_column("Extension", style="bold blue")
    table.add_column("Files", justify="right", style="cyan")
    table.add_column("Total Size (MB)", justify="right", style="yellow")
    table.add_column("Avg Size (MB)", justify="right", style="magenta")
    
    for ext, row in ext_summary.head(15).iterrows():
        table.add_row(
            ext,
            f"{int(row['File Count']):,}",
            f"{row['Total Size (MB)']:,.2f}",
            f"{row['Avg Size (MB)']:,.2f}"
        )
    
    console.print(table)
    console.print()

def create_visualizations(df):
    """Create beautiful visualizations"""
    # Set up the plotting style
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(20, 15))
    fig.patch.set_facecolor('#0a0a0a')
    
    # 1. Files by folder (top 10)
    plt.subplot(2, 3, 1)
    folder_counts = df['folder'].value_counts().head(10)
    bars = plt.bar(range(len(folder_counts)), folder_counts.values, 
                   color=plt.cm.viridis(np.linspace(0, 1, len(folder_counts))))
    plt.title('📁 Files by Folder (Top 10)', fontsize=14, color='white', pad=20)
    plt.ylabel('Number of Files', color='white')
    plt.xticks(range(len(folder_counts)), folder_counts.index, rotation=45, ha='right', color='white')
    plt.yticks(color='white')
    
    # 2. File size distribution by folder
    plt.subplot(2, 3, 2)
    folder_sizes = df.groupby('folder')['size_mb'].sum().sort_values(ascending=False).head(10)
    bars = plt.bar(range(len(folder_sizes)), folder_sizes.values,
                   color=plt.cm.plasma(np.linspace(0, 1, len(folder_sizes))))
    plt.title('💾 Total Size by Folder (Top 10)', fontsize=14, color='white', pad=20)
    plt.ylabel('Size (MB)', color='white')
    plt.xticks(range(len(folder_sizes)), folder_sizes.index, rotation=45, ha='right', color='white')
    plt.yticks(color='white')
    
    # 3. File types distribution
    plt.subplot(2, 3, 3)
    ext_counts = df['extension'].value_counts().head(10)
    colors = plt.cm.Set3(np.linspace(0, 1, len(ext_counts)))
    plt.pie(ext_counts.values, labels=ext_counts.index, autopct='%1.1f%%', 
            colors=colors, startangle=90)
    plt.title('📄 File Types Distribution', fontsize=14, color='white', pad=20)
    
    # 4. File size histogram
    plt.subplot(2, 3, 4)
    # Filter out very large files for better visualization
    size_data = df[df['size_mb'] < df['size_mb'].quantile(0.95)]['size_mb']
    plt.hist(size_data, bins=50, color='skyblue', alpha=0.7, edgecolor='white')
    plt.title('📊 File Size Distribution', fontsize=14, color='white', pad=20)
    plt.xlabel('Size (MB)', color='white')
    plt.ylabel('Frequency', color='white')
    plt.xticks(color='white')
    plt.yticks(color='white')
    
    # 5. Files over time (by modification date)
    plt.subplot(2, 3, 5)
    df['month_year'] = df['modified_date'].dt.to_period('M')
    monthly_counts = df['month_year'].value_counts().sort_index().tail(12)
    plt.plot(range(len(monthly_counts)), monthly_counts.values, 
             marker='o', linewidth=2, markersize=6, color='orange')
    plt.title('📅 Files Modified Over Time (Last 12 Months)', fontsize=14, color='white', pad=20)
    plt.ylabel('Number of Files', color='white')
    plt.xticks(range(len(monthly_counts)), [str(x) for x in monthly_counts.index], 
               rotation=45, ha='right', color='white')
    plt.yticks(color='white')
    plt.grid(True, alpha=0.3)
    
    # 6. Largest files
    plt.subplot(2, 3, 6)
    largest_files = df.nlargest(10, 'size_mb')
    bars = plt.barh(range(len(largest_files)), largest_files['size_mb'].values,
                    color=plt.cm.Reds(np.linspace(0.3, 1, len(largest_files))))
    plt.title('🎯 Largest Files', fontsize=14, color='white', pad=20)
    plt.xlabel('Size (MB)', color='white')
    plt.yticks(range(len(largest_files)), 
               [f[:30] + '...' if len(f) > 30 else f for f in largest_files['filename']], 
               color='white')
    plt.xticks(color='white')
    
    plt.tight_layout()
    plt.savefig('dir_analysis.png', dpi=300, bbox_inches='tight', 
                facecolor='#0a0a0a', edgecolor='none')
    plt.show()

def save_detailed_csv(df):
    """Save detailed file list to CSV"""
    # Create a clean version for CSV
    csv_df = df.copy()
    csv_df['size_gb'] = csv_df['size_mb'] / 1024
    csv_df = csv_df.sort_values(['folder', 'size_mb'], ascending=[True, False])
    
    # Select relevant columns
    csv_df = csv_df[['folder', 'filename', 'extension', 'size_mb', 'size_gb', 
                     'modified_date', 'full_path']]
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'dir_file_inventory_{timestamp}.csv'
    csv_df.to_csv(filename, index=False)
    
    console = Console()
    console.print(f"\n💾 Detailed file inventory saved to: [bold green]{filename}[/bold green]")

def main():
    dir_path = sys.argv[1]
    
    try:
        save = sys.argv[2]
    except IndexError:
        save = False
    
    console = Console()
    console.print(f"[bold cyan]🔍 Analyzing {dir_path} Folder...[/bold cyan]\n")
    
    # Check if path exists
    if not os.path.exists(dir_path):
        console.print(f"[bold red]❌ Path not found: {dir_path}[/bold red]")
        return
    
    # Scan files
    df = get_file_info(dir_path)
    
    if df.empty:
        console.print("[bold yellow]⚠️  No files found![/bold yellow]")
        return
    
    # Display summary tables
    create_summary_table(df)
    create_folder_breakdown_table(df)
    create_file_type_table(df)
    
    # Create visualizations
    console.print("[bold green]📊 Creating visualizations...[/bold green]")
    create_visualizations(df)
    
    # Save detailed CSV
    if save:
        save_detailed_csv(df)
    else:
        console.print("[bold yellow]⚠️  Detailed CSV not saved![/bold yellow]")
    
    console.print("\n[bold green]✨ Analysis complete! Check the generated files:[/bold green]")
    console.print("📊 dir_analysis.png - Visual charts")
    console.print("📋 dir_file_inventory_*.csv - Detailed file list")

if __name__ == "__main__":
    main()