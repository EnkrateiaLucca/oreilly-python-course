#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "openai>=1.30.1",
#   "pydantic>=2.7.1",
# ]
# ///

from pathlib import Path
from openai import OpenAI
from pydantic import BaseModel
import sys

# --- OpenAI setup
client = OpenAI()

# --- Pydantic model
class InvoiceData(BaseModel):
    name: str
    date: str
    tax_id: str

# --- Change this path or pass via command line
FOLDER = Path("/Users/greatmaster/Desktop/projects/oreilly-live-trainings/oreilly-python-course/notebooks/assets/fake-invoices")
if len(sys.argv) > 1:
    FOLDER = Path(sys.argv[1])

def extract_from_file(file_path: Path):
    content = file_path.read_text(encoding="utf-8")
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "Extract the invoice name, date, and tax ID."},
                {"role": "user", "content": content},
            ],
            response_format=InvoiceData,
        )
        return response.choices[0].message.parsed
    except Exception as e:
        print(f"❌ {file_path.name}: {e}")
        return None

def main():
    if not FOLDER.exists():
        print(f"⚠️ Folder not found: {FOLDER}")
        return

    txt_files = list(FOLDER.glob("*.txt"))
    if not txt_files:
        print("⚠️ No .txt files found in the folder.")
        return

    print(f"📂 Processing {len(txt_files)} files in {FOLDER}...\n")

    for file in txt_files:
        data = extract_from_file(file)
        if data:
            print(f"✅ {file.name}: {data}\n")

if __name__ == "__main__":
    main()