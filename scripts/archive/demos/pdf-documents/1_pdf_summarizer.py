# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pymupdf",
#     "openai",
# ]
# ///

import urllib.request
import sys
from openai import OpenAI
import fitz


def download_pdf(url: str, filepath: str) -> str:
    """Download a PDF from a URL to a local filepath."""
    urllib.request.urlretrieve(url, filepath)
    print(f"Downloaded paper to {filepath}")
    return filepath


def extract_text_from_pdf(filepath: str) -> str:
    """Extract text content from a PDF file."""
    doc = fitz.open(filepath)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    print(f"Extracted {len(text)} characters from PDF")
    return text

def summarize_pdf(text: str) -> str:
    """Summarize the pdf text"""
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "user",
                "content": f"Summarize the following text: {text} into bullet points."
            }
        ],
        )
    
    return response.choices[0].message.content
    
    
    

# downloads the pdf and saves it to the current directory
# input_url = input("Enter the URL of the pdf to summarize: ") # takes input from the user when the user runs the script but manually

input_url = sys.argv[1]

pdf_path = download_pdf(input_url, "./paper.pdf")

# extract the text
text = extract_text_from_pdf(pdf_path)

# summarize the text
summary = summarize_pdf(text)

print(summary)