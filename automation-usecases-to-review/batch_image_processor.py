#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pillow>=10.0.0",
#     "rich>=13.0.0",
# ]
# ///
"""
Batch Image Processor - Resize, convert, compress images in bulk
Usage: python batch_image_processor.py [directory] [--resize 1920x1080] [--format jpg] [--quality 85]
"""

import os
from pathlib import Path
from typing import Tuple, Optional
import argparse
from PIL import Image, ImageEnhance
from rich.console import Console
from rich.progress import track
from rich.table import Table

console = Console()

SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}


def get_file_size_str(size_bytes: int) -> str:
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def parse_dimensions(dim_str: str) -> Tuple[int, int]:
    """Parse dimension string like '1920x1080' into tuple."""
    try:
        width, height = dim_str.lower().split('x')
        return int(width), int(height)
    except:
        raise ValueError(f"Invalid dimension format: {dim_str}. Use format like '1920x1080'")


def resize_image(img: Image.Image, target_size: Tuple[int, int], maintain_aspect: bool = True) -> Image.Image:
    """Resize image to target size."""
    if maintain_aspect:
        img.thumbnail(target_size, Image.Resampling.LANCZOS)
        return img
    else:
        return img.resize(target_size, Image.Resampling.LANCZOS)


def compress_image(img: Image.Image, quality: int = 85) -> Image.Image:
    """Compress image (mainly affects JPEG)."""
    return img


def convert_format(img: Image.Image, target_format: str) -> Image.Image:
    """Convert image to target format."""
    if target_format.upper() == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
        # Convert transparency to white background for JPEG
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        return background
    elif target_format.upper() != 'JPEG' and img.mode == 'RGB':
        # Convert to RGBA for formats that support transparency
        return img.convert('RGBA')
    return img


def add_watermark(img: Image.Image, text: str, position: str = 'bottom-right') -> Image.Image:
    """Add text watermark to image."""
    from PIL import ImageDraw, ImageFont

    draw = ImageDraw.Draw(img)

    # Try to use a decent font, fallback to default
    try:
        font_size = int(img.height * 0.03)
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        font = ImageFont.load_default()

    # Calculate text position
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    margin = int(img.height * 0.02)

    if position == 'bottom-right':
        x = img.width - text_width - margin
        y = img.height - text_height - margin
    elif position == 'bottom-left':
        x = margin
        y = img.height - text_height - margin
    elif position == 'top-right':
        x = img.width - text_width - margin
        y = margin
    else:  # top-left
        x = margin
        y = margin

    # Draw text with shadow for better visibility
    draw.text((x + 2, y + 2), text, fill=(0, 0, 0, 128), font=font)
    draw.text((x, y), text, fill=(255, 255, 255, 180), font=font)

    return img


def process_image(
    input_path: Path,
    output_dir: Path,
    target_size: Optional[Tuple[int, int]] = None,
    target_format: Optional[str] = None,
    quality: int = 85,
    maintain_aspect: bool = True,
    watermark: Optional[str] = None,
    watermark_position: str = 'bottom-right'
) -> dict:
    """Process a single image with specified operations."""
    try:
        with Image.open(input_path) as img:
            original_size = input_path.stat().st_size

            # Resize if requested
            if target_size:
                img = resize_image(img, target_size, maintain_aspect)

            # Add watermark if requested
            if watermark:
                img = add_watermark(img, watermark, watermark_position)

            # Determine output format
            if target_format:
                output_format = target_format.upper()
                output_ext = f".{target_format.lower()}"
            else:
                output_format = img.format or 'PNG'
                output_ext = input_path.suffix

            # Convert format if needed
            img = convert_format(img, output_format)

            # Save processed image
            output_path = output_dir / f"{input_path.stem}{output_ext}"

            # Handle duplicates
            counter = 1
            while output_path.exists():
                output_path = output_dir / f"{input_path.stem}_{counter}{output_ext}"
                counter += 1

            save_kwargs = {}
            if output_format in ('JPEG', 'JPG'):
                save_kwargs['quality'] = quality
                save_kwargs['optimize'] = True
            elif output_format == 'PNG':
                save_kwargs['optimize'] = True

            img.save(output_path, format=output_format, **save_kwargs)

            new_size = output_path.stat().st_size

            return {
                'success': True,
                'input_path': input_path,
                'output_path': output_path,
                'original_size': original_size,
                'new_size': new_size,
                'compression_ratio': (1 - new_size / original_size) * 100 if original_size > 0 else 0
            }

    except Exception as e:
        return {
            'success': False,
            'input_path': input_path,
            'error': str(e)
        }


def process_directory(
    input_dir: Path,
    output_dir: Path,
    target_size: Optional[Tuple[int, int]] = None,
    target_format: Optional[str] = None,
    quality: int = 85,
    maintain_aspect: bool = True,
    watermark: Optional[str] = None,
    watermark_position: str = 'bottom-right',
    recursive: bool = False
) -> list:
    """Process all images in a directory."""

    # Find all image files
    if recursive:
        image_files = []
        for ext in SUPPORTED_FORMATS:
            image_files.extend(input_dir.rglob(f"*{ext}"))
    else:
        image_files = [f for f in input_dir.iterdir()
                      if f.suffix.lower() in SUPPORTED_FORMATS]

    if not image_files:
        console.print("[yellow]No image files found![/yellow]")
        return []

    console.print(f"\n[cyan]Found {len(image_files)} images to process[/cyan]\n")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process images
    results = []
    for image_path in track(image_files, description="Processing images..."):
        result = process_image(
            image_path,
            output_dir,
            target_size,
            target_format,
            quality,
            maintain_aspect,
            watermark,
            watermark_position
        )
        results.append(result)

    return results


def display_results(results: list):
    """Display processing results in a nice table."""
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]

    if successful:
        table = Table(title="Processing Results", show_header=True)
        table.add_column("File", style="cyan")
        table.add_column("Original", style="yellow", justify="right")
        table.add_column("New", style="green", justify="right")
        table.add_column("Saved", style="magenta", justify="right")

        total_original = 0
        total_new = 0

        for result in successful[:20]:  # Show first 20
            original_size = result['original_size']
            new_size = result['new_size']
            compression = result['compression_ratio']

            total_original += original_size
            total_new += new_size

            table.add_row(
                result['input_path'].name,
                get_file_size_str(original_size),
                get_file_size_str(new_size),
                f"{compression:.1f}%"
            )

        if len(successful) > 20:
            table.add_row("...", "...", "...", "...")

        table.add_row(
            "TOTAL",
            get_file_size_str(total_original),
            get_file_size_str(total_new),
            f"{((1 - total_new / total_original) * 100 if total_original > 0 else 0):.1f}%",
            style="bold yellow"
        )

        console.print(table)
        console.print(f"\n[green]Successfully processed {len(successful)} images[/green]")
        console.print(f"[green]Total space saved: {get_file_size_str(total_original - total_new)}[/green]")

    if failed:
        console.print(f"\n[red]Failed to process {len(failed)} images:[/red]")
        for result in failed[:10]:  # Show first 10 failures
            console.print(f"  {result['input_path']}: {result['error']}")


def main():
    parser = argparse.ArgumentParser(
        description="Batch Image Processor - Process multiple images at once"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory containing images (default: current directory)"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output directory (default: ./processed)"
    )
    parser.add_argument(
        "--resize",
        type=str,
        help="Resize images to dimensions (e.g., '1920x1080')"
    )
    parser.add_argument(
        "--format",
        choices=["jpg", "png", "webp", "gif", "bmp"],
        help="Convert images to format"
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=85,
        help="JPEG quality (1-100, default: 85)"
    )
    parser.add_argument(
        "--no-aspect",
        action="store_true",
        help="Don't maintain aspect ratio when resizing"
    )
    parser.add_argument(
        "--watermark",
        type=str,
        help="Add text watermark to images"
    )
    parser.add_argument(
        "--watermark-position",
        choices=["bottom-right", "bottom-left", "top-right", "top-left"],
        default="bottom-right",
        help="Watermark position (default: bottom-right)"
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Process subdirectories recursively"
    )

    args = parser.parse_args()

    input_dir = Path(args.directory).resolve()
    output_dir = Path(args.output).resolve() if args.output else input_dir / "processed"

    if not input_dir.exists():
        console.print(f"[red]Error: Directory '{input_dir}' does not exist[/red]")
        return

    # Parse resize dimensions if provided
    target_size = None
    if args.resize:
        try:
            target_size = parse_dimensions(args.resize)
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            return

    console.print(f"\n[bold cyan]Batch Image Processor[/bold cyan]")
    console.print(f"Input: {input_dir}")
    console.print(f"Output: {output_dir}")
    if target_size:
        console.print(f"Resize: {target_size[0]}x{target_size[1]}")
    if args.format:
        console.print(f"Format: {args.format.upper()}")
    console.print(f"Quality: {args.quality}")
    if args.watermark:
        console.print(f"Watermark: '{args.watermark}' at {args.watermark_position}")

    # Process images
    results = process_directory(
        input_dir,
        output_dir,
        target_size,
        args.format,
        args.quality,
        not args.no_aspect,
        args.watermark,
        args.watermark_position,
        args.recursive
    )

    # Display results
    if results:
        display_results(results)
        console.print(f"\n[green]Processed images saved to: {output_dir}[/green]")


if __name__ == "__main__":
    main()
