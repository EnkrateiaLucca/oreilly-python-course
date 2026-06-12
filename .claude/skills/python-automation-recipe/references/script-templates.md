# Script Templates by Category

Adapt these skeletons when generating scripts in Step 4a/4b. All follow Lucas's course conventions: uv inline metadata, argparse CLI, small typed functions, AI verification, idempotency, dry-run for destructive ops.

Pick the section matching the chosen category. Don't dump the whole file — copy only the relevant skeleton and tailor it to the student's specific I→P→O.

---

## 1. Files & Folders

Used for: organize, rename, dedupe, backup, classify by metadata.

Key conventions:
- Always offer `--dry-run` (default **on** if it deletes or moves).
- Idempotent: rerunning does not corrupt — handle name conflicts with numeric suffix or skip.
- Print a final summary of counts.

```python
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Organize files in a folder by extension."""
import argparse
import shutil
from pathlib import Path

DOCUMENTS = {".md", ".txt", ".pdf"}
MEDIA = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def classify(ext: str) -> str:
    if ext in DOCUMENTS:
        return "documents"
    if ext in MEDIA:
        return "media"
    return "others"


def unique_dest(dest: Path) -> Path:
    if not dest.exists():
        return dest
    n = 1
    while True:
        candidate = dest.with_name(f"{dest.stem}({n}){dest.suffix}")
        if not candidate.exists():
            return candidate
        n += 1


def organize(folder: Path, dry_run: bool) -> dict[str, int]:
    counts = {"documents": 0, "media": 0, "others": 0}
    for entry in folder.iterdir():
        if not entry.is_file():
            continue
        bucket = classify(entry.suffix.lower())
        target_dir = folder / bucket
        if not dry_run:
            target_dir.mkdir(exist_ok=True)
        dest = unique_dest(target_dir / entry.name)
        action = "WOULD MOVE" if dry_run else "MOVED"
        print(f"{action}: {entry.name} -> {bucket}/")
        if not dry_run:
            shutil.move(str(entry), str(dest))
        counts[bucket] += 1
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="organize_folder",
        description="Sort top-level files in FOLDER into documents/, media/, others/.",
    )
    parser.add_argument("folder", type=Path, help="Folder to organize")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Show what would happen without moving files (default).")
    parser.add_argument("--execute", action="store_true",
                        help="Actually move files. Overrides --dry-run.")
    args = parser.parse_args()
    if not args.folder.is_dir():
        raise SystemExit(f"Not a directory: {args.folder}")
    dry = not args.execute
    counts = organize(args.folder, dry)
    print(f"\nDone. {'(dry run)' if dry else ''} {counts}")


if __name__ == "__main__":
    main()
```

---

## 2. PDF / Documents

Used for: summarize, extract fields, chat with a doc.

Key conventions:
- Print raw AI output before parsing — silent wrongness is the #1 failure mode.
- Ask LLM for **JSON** when downstream code consumes the result.
- Validate the parsed JSON with a small schema (key presence, type) before using it.

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["openai", "pypdf2"]
# ///
"""Summarize a PDF into bullet points using an LLM."""
import argparse
import os
import sys
from pathlib import Path
from openai import OpenAI
from PyPDF2 import PdfReader


def load_pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join(p.extract_text() or "" for p in reader.pages)


def ask_ai(prompt: str, model: str = "gpt-5-mini") -> str:
    client = OpenAI()
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="summarize_pdf",
        description="Summarize a PDF into instructive bullet points.",
    )
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--model", default="gpt-5-mini")
    args = parser.parse_args()
    if not args.pdf.exists():
        raise SystemExit(f"No such file: {args.pdf}")
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Set OPENAI_API_KEY first.")

    text = load_pdf_text(args.pdf)
    print(f"[loaded {len(text)} chars from {args.pdf.name}]")
    prompt = f"Summarize the following into compressed instructive bullet points:\n\n{text}"
    output = ask_ai(prompt, args.model)

    print("\n--- AI RAW OUTPUT (verify before trusting) ---")
    print(output)


if __name__ == "__main__":
    main()
```

For **structured extraction** (invoices, receipts), prompt the model to return JSON and parse defensively:

```python
import json

def extract_invoice(text: str) -> dict:
    prompt = (
        "Extract these fields from the invoice text. "
        "Respond with ONLY a JSON object — no prose, no code fences. "
        'Keys: {"vendor": str, "date": "YYYY-MM-DD", "total": float, "currency": str}\n\n'
        f"{text}"
    )
    raw = ask_ai(prompt)
    print(f"[raw model output]\n{raw}\n")
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    data = json.loads(cleaned)
    # rule-based sanity checks — catches silent wrongness
    assert isinstance(data.get("total"), (int, float)), "total must be numeric"
    assert len(data.get("date", "")) == 10, "date must be YYYY-MM-DD"
    return data
```

---

## 3. Data / Dashboards

Used for: CSV summary, chart from data, ETL.

Key conventions:
- pandas + matplotlib, no seaborn unless asked.
- Always print `df.head()` and shape before the heavy step.
- Save chart with explicit path; do not call `plt.show()` in a CLI script.

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["pandas", "matplotlib"]
# ///
"""Build a simple sales-by-month chart from a CSV."""
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def load_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    print(f"[loaded] shape={df.shape}")
    print(df.head())
    return df


def plot_monthly(df: pd.DataFrame, out: Path) -> None:
    monthly = df.groupby(df["date"].dt.to_period("M"))["amount"].sum()
    ax = monthly.plot(kind="bar", title="Sales by month")
    ax.set_ylabel("Amount")
    plt.tight_layout()
    plt.savefig(out, dpi=120)
    print(f"[saved] {out}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="monthly_sales",
                                     description="Plot total sales per month from CSV with date,amount columns.")
    parser.add_argument("csv", type=Path)
    parser.add_argument("--out", type=Path, default=Path("monthly_sales.png"))
    args = parser.parse_args()
    df = load_csv(args.csv)
    plot_monthly(df, args.out)


if __name__ == "__main__":
    main()
```

---

## 4. Browser Automation (Playwright)

Used for: scrape, fill forms, login flows.

**Yellow zone by default.** Add the warning header. Encourage manual runs first.

Key conventions:
- `headless=False` while developing, switch with a flag.
- Wait for selectors, never `sleep()`.
- Inline warning about TOS + selector rot.

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["playwright"]
# ///
"""Scrape titles from a public listing page.

WARNING: Browser automation is fragile. Selectors break when the site updates.
Re-check the site's Terms of Service before scheduling this. Watch the first
~10 runs by hand before trusting the output.
"""
import argparse
from playwright.sync_api import sync_playwright


def scrape_titles(url: str, headless: bool) -> list[str]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_selector("h2.title")
        titles = [el.inner_text() for el in page.query_selector_all("h2.title")]
        browser.close()
    return titles


def main() -> None:
    parser = argparse.ArgumentParser(prog="scrape_titles",
                                     description="Scrape h2.title text from a URL (yellow zone — watch the output).")
    parser.add_argument("url")
    parser.add_argument("--headed", action="store_true", help="Show the browser window")
    args = parser.parse_args()
    titles = scrape_titles(args.url, headless=not args.headed)
    print(f"[found {len(titles)} titles]")
    for t in titles:
        print(f"- {t}")


if __name__ == "__main__":
    main()
```

Reminder to surface to the student: `uv run playwright install` is needed once.

---

## 5. Email / Comms

Used for: classify, summarize, RSS digest.

Key conventions:
- Reading IMAP/RSS is green. Sending mail is yellow at minimum (red if no human review).
- Always default to writing to a Drafts folder / local file, never auto-send.

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["anthropic", "feedparser"]
# ///
"""Pull headlines from an RSS feed and summarize them with Claude."""
import argparse
import os
import feedparser
import anthropic


def fetch_headlines(url: str, limit: int) -> list[str]:
    feed = feedparser.parse(url)
    return [entry.title for entry in feed.entries[:limit]]


def summarize(headlines: list[str], model: str) -> str:
    client = anthropic.Anthropic()
    joined = "\n- ".join(headlines)
    prompt = (
        "Group these headlines into 3 themes and give a one-line takeaway "
        f"for each. Headlines:\n- {joined}"
    )
    resp = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text


def main() -> None:
    parser = argparse.ArgumentParser(prog="news_digest",
                                     description="Fetch RSS headlines and summarize themes with Claude.")
    parser.add_argument("feed_url")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--model", default="claude-sonnet-4-6")
    args = parser.parse_args()
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise SystemExit("Set ANTHROPIC_API_KEY first.")
    headlines = fetch_headlines(args.feed_url, args.limit)
    print(f"[got {len(headlines)} headlines]")
    summary = summarize(headlines, args.model)
    print("\n--- AI SUMMARY (verify before sharing) ---")
    print(summary)


if __name__ == "__main__":
    main()
```

---

## 6. AI-Powered Text (generic)

When the task is "summarize / classify / extract from text" and doesn't fit a category above, use this minimal pattern:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["openai"]
# ///
"""Classify a chunk of text into one of N categories."""
import argparse
import json
import os
import sys
from openai import OpenAI

CATEGORIES = ["urgent", "normal", "promotional", "spam"]


def ask_ai(prompt: str, model: str = "gpt-5-mini") -> str:
    return OpenAI().chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    ).choices[0].message.content


def classify(text: str, model: str) -> dict:
    prompt = (
        f"Classify the text into exactly one of {CATEGORIES}. "
        'Reply with JSON: {"label": str, "confidence": float, "reason": str}\n\n'
        f"TEXT:\n{text}"
    )
    raw = ask_ai(prompt, model)
    print(f"[raw]\n{raw}\n")
    data = json.loads(raw.replace("```json", "").replace("```", "").strip())
    assert data["label"] in CATEGORIES, f"Unknown label: {data['label']}"
    return data


def main() -> None:
    parser = argparse.ArgumentParser(prog="classify_text",
                                     description="Classify text from stdin or a file into a fixed set of labels.")
    parser.add_argument("--file", help="Read text from this file instead of stdin.")
    parser.add_argument("--model", default="gpt-5-mini")
    args = parser.parse_args()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Set OPENAI_API_KEY first.")
    text = open(args.file).read() if args.file else sys.stdin.read()
    print(json.dumps(classify(text, args.model), indent=2))


if __name__ == "__main__":
    main()
```

---

## Scheduling snippets (mention only if student said "run on a schedule")

**macOS — quick cron line** (`crontab -e`):
```
0 9 * * * /usr/local/bin/uv run --quiet python /full/path/script.py >> /tmp/script.log 2>&1
```

**macOS — launchd plist** (`~/Library/LaunchAgents/com.lucas.myscript.plist`):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict>
  <key>Label</key><string>com.lucas.myscript</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/bin/uv</string><string>run</string>
    <string>python</string><string>/full/path/script.py</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer></dict>
  <key>StandardOutPath</key><string>/tmp/myscript.log</string>
  <key>StandardErrorPath</key><string>/tmp/myscript.err</string>
</dict></plist>
```
Load with `launchctl load ~/Library/LaunchAgents/com.lucas.myscript.plist`.

**Linux**: same crontab line as macOS.
**Windows**: Task Scheduler GUI is the path of least resistance for students — don't try to script it.

Reminder: never schedule a yellow-zone script. Run it manually until you trust it.
