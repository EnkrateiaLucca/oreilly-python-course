# /// script
# requires-python = ">=3.10"
# ///
"""Turn a plain Markdown file into a browser slide deck (no PowerPoint needed).

Automation category: CLI tools.

Input   -> a Markdown file where slides are separated by a line with just '---'
Process -> hand the Markdown to Marp, which renders it into a slide deck
Output  -> a single self-contained .html file you can open and present

This is the classic "wrap a CLI tool" automation: instead of building the slide
engine ourselves, we let Marp (https://marp.app) do the heavy lifting -- rendering
Markdown, arrow-key navigation, slide numbers, fullscreen ('f'), presenter view
('p') -- and Python just prepares the input, calls the tool, and opens the result.

Marp ships as a Node CLI. We run it through `npx` so there is nothing to install
globally; the first run downloads it (needs internet), after that it's cached.

Run it like:
    uv run scripts/demos/cli-tools/slides.py scripts/demos/cli-tools/sample_slides.md
    uv run scripts/demos/cli-tools/slides.py my_talk.md --output talk.html --theme gaia

Write your Markdown like this (three dashes on their own line start a new slide):

    # My Talk

    ---

    ## Point one
    - bullet
    - bullet

Needs: Node.js (for `npx`). No API key. The first run pulls the Marp CLI from npm,
so you need internet that one time.
"""

import argparse
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

# Marp turns on its slide features when the Markdown has this front matter at the
# top. We prepend it automatically (unless the file already has its own), so the
# same plain Markdown that worked before keeps working.
#   marp: true     -> enable Marp rendering
#   paginate: true -> show slide numbers
#   theme/style    -> a clean look that matches the old deck
FRONT_MATTER = """---
marp: true
paginate: true
theme: {theme}
style: |
  section {{ font-family: -apple-system, system-ui, sans-serif; font-size: 24px; }}
  h1, h2, h3 {{ font-weight: 600; }}
  code {{ font-family: "Menlo", monospace; }}
---

"""


def build_deck(markdown_path: Path, output_path: Path, theme: str) -> None:
    # 1. Read the content the user wrote.
    markdown = markdown_path.read_text(encoding="utf-8")

    # 2. Count slides just to give friendly feedback. Marp treats a line that is
    #    exactly '---' as a slide break, so slides = separators + 1.
    slide_count = markdown.count("\n---\n") + 1

    # 3. Make sure Marp's front matter is present. If the file already starts with
    #    its own '---' front matter we leave it alone; otherwise we prepend ours.
    if not markdown.lstrip().startswith("---"):
        markdown = FRONT_MATTER.format(theme=theme) + markdown

    # 4. Write the prepared Markdown to a temp file next to the output, then hand
    #    it to the Marp CLI via `npx` (no global install needed).
    prepared = output_path.with_suffix(".marp.md")
    prepared.write_text(markdown, encoding="utf-8")

    cmd = [
        "npx", "--yes", "@marp-team/marp-cli@latest",
        str(prepared),
        "-o", str(output_path),
        "--html",  # allow raw HTML in the Markdown
    ]
    print("Rendering with Marp (first run downloads the CLI)...")
    result = subprocess.run(cmd)
    prepared.unlink(missing_ok=True)  # tidy up the temp file

    if result.returncode != 0:
        sys.exit("Marp failed to build the deck. Is Node.js installed (needed for npx)?")

    print(f"Built {slide_count} slide(s) -> {output_path}")
    print("Open it in a browser and use the arrow keys to present. Press 'p' for presenter notes, 'f' for fullscreen.")

    # 5. Open the finished deck in the default browser so it's ready to present.
    webbrowser.open(output_path.resolve().as_uri())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build a Marp slide deck from a Markdown file.")
    parser.add_argument("markdown", help="Path to your Markdown file (slides separated by '---').")
    parser.add_argument("--output", help="Where to write the .html (default: same name as the input).")
    parser.add_argument("--theme", default="default", help="Marp theme: default, gaia, or uncover.")
    args = parser.parse_args()

    if shutil.which("npx") is None:
        sys.exit("Couldn't find `npx`. Install Node.js (https://nodejs.org) to use Marp.")

    markdown_path = Path(args.markdown).expanduser()
    output_path = Path(args.output).expanduser() if args.output else markdown_path.with_suffix(".html")

    build_deck(markdown_path, output_path, args.theme)