#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests",
#   "pypdf"
# ]
# ///
"""
Standalone script to download abstracts or first pages of ArXiv papers.
Usage:
    uv run download_arxiv.py urls.txt --mode abstract
    uv run download_arxiv.py urls.txt --mode firstpage
"""

import argparse
import os
import re
import requests
from pypdf import PdfReader
from io import BytesIO


# ----------------------------------------
# Extracts the arXiv ID from a URL
# Input: "https://arxiv.org/abs/2310.15511"
# Output: "2310.15511"
# ----------------------------------------
def extract_arxiv_id(url: str) -> str:
    m = re.search(r"arxiv\.org\/abs\/([\w\.\/\-]+)", url.strip())
    return m.group(1) if m else None


# ----------------------------------------
# Fetches title + abstract from ArXiv API
# Input: arxiv_id ("2310.15511")
# Process: calls API, extracts <title> + <summary>
# Output: dict with id, title, abstract
# ----------------------------------------
def fetch_metadata(arxiv_id: str) -> dict:
    api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    r = requests.get(api_url, timeout=10)
    if r.status_code != 200:
        raise RuntimeError(f"Failed to fetch metadata for {arxiv_id}")

    # Extract relevant fields from XML
    abstract_match = re.search(r"<summary>(.*?)</summary>", r.text, re.S)
    title_match = re.search(r"<title>(.*?)</title>", r.text, re.S)

    abstract = abstract_match.group(1).strip() if abstract_match else "No abstract found."
    title = title_match.group(1).strip() if title_match else "No title found."

    return {
        "id": arxiv_id,
        "title": title,
        "abstract": abstract
    }


# ----------------------------------------
# Downloads PDF + extracts the first page
# Input: arxiv_id + output path
# Process: fetch PDF, load with pypdf, get page 1 text
# Output: text file containing first-page content
# ----------------------------------------
def download_pdf_first_page(arxiv_id: str, output_path: str):
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    pdf_bytes = requests.get(pdf_url, timeout=15)
    if pdf_bytes.status_code != 200:
        raise RuntimeError(f"Could not download PDF for {arxiv_id}")

    reader = PdfReader(BytesIO(pdf_bytes.content))
    first_page = reader.pages[0]
    text = first_page.extract_text() or ""

    # Save first page text
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)


# ----------------------------------------
# MAIN SCRIPT LOGIC
# Input: filename with ArXiv URLs + mode ("abstract" or "firstpage")
# Process: iterate through URLs → extract ID → process accordingly
# Output: one text file per paper in outputs/
# ----------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help=".txt file with ArXiv URLs")
    parser.add_argument("--mode", choices=["abstract", "firstpage"], default="abstract")
    
    args = parser.parse_args()

    # Read list of URLs from text file
    with open(args.file, "r", encoding="utf-8") as f:
        urls = f.readlines()

    # Create output directory
    os.makedirs("outputs", exist_ok=True)

    for url in urls:
        arxiv_id = extract_arxiv_id(url)
        if not arxiv_id:
            print(f"Skipping invalid line: {url.strip()}")
            continue

        print(f"Processing {arxiv_id}...")

        # --------- Mode: Save Abstract ---------
        if args.mode == "abstract":
            meta = fetch_metadata(arxiv_id)
            out_path = os.path.join("outputs", f"{arxiv_id}_abstract.txt")

            # Save metadata (title + abstract)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(f"Title: {meta['title']}\n\n")
                f.write(meta["abstract"])

            print(f"Saved abstract → {out_path}")

        # --------- Mode: Save First PDF Page ---------
        elif args.mode == "firstpage":
            out_path = os.path.join("outputs", f"{arxiv_id}_firstpage.txt")
            download_pdf_first_page(arxiv_id, out_path)
            print(f"Saved first page → {out_path}")


if __name__ == "__main__":
    main()