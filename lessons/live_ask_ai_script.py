# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "openai",
# ]
# ///

import csv
from datetime import datetime
from pathlib import Path
import sys

from openai import OpenAI

MODEL = "gpt-5.6"
LOG_FILE = Path("openai_history.csv")


def ask_openai(question: str) -> str:
    client = OpenAI()

    response = client.responses.create(
        model=MODEL,
        input=question,
    )

    return response.output_text.strip()


def log_message(question: str, answer: str) -> None:
    file_exists = LOG_FILE.exists()

    with LOG_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["timestamp", "model", "question", "answer"])

        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            MODEL,
            question,
            answer,
        ])


def main():
    if len(sys.argv) < 2:
        print('Usage: uv run ask_openai.py "your question"')
        return

    question = " ".join(sys.argv[1:])

    answer = ask_openai(question)

    print("\n── GPT-5.6 ──────────────────────────────\n")
    print(answer)
    print("\n─────────────────────────────────────────")

    log_message(question, answer)

    print(f"\n✓ Saved to {LOG_FILE}")


if __name__ == "__main__":
    main()