# # Prompt used:
# I want to create an. automation that given a url for a pdf it will:

# Download the paper locally as demonstrated in this example:
# import urllib.request
# url = "https://proceedings.neurips.cc/paper_files/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf"
# filepath = "../assets/paper3.pdf"
# urllib.request.urlretrieve(url, filepath)
# print("Downloaded paper")

# It will load the contents of the pdf ?

# It will use the OpenAI API to summarize that pdf similar to what you can see in this example:
# from openai import OpenAI
# def ask_ai(prompt, model_name="gpt-5-mini"):
#  # access the openai API and call this model to get a response
#  client = OpenAI()
#  response = client.chat.completions.create(
#      messages=[
#          {
#              "role": "user",
#               "content": prompt
#          }
#      ],
#      model=model_name
#  )
#  output = response.choices[0].message.content
#  print(output)
#  return output
# I also want to be able to run this script with uv using inline metadata 
# https://docs.astral.sh/uv/guides/scripts/

# just add the necessary metadata

# THe output summary should be saved as a .md file with the name of the paper separated by dashes
# AI Tools used: Claude 4.5 Opus chatbot


# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pymupdf",
#     "openai",
# ]
# ///

import urllib.request
import os
import re
from openai import OpenAI
import fitz  # PyMuPDF


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


def ask_ai(prompt: str, model_name: str = "gpt-4o-mini") -> str:
    """Call OpenAI API to get a response."""
    client = OpenAI()
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        model=model_name
    )
    output = response.choices[0].message.content
    return output


def summarize_pdf(pdf_text: str, model_name: str = "gpt-4o-mini") -> str:
    """Generate a summary of the PDF content using OpenAI."""
    prompt = f"""Please provide a comprehensive summary of the following academic paper. 
Include:
- Main objective/research question
- Key methodology
- Main findings/results
- Conclusions and implications

Paper content:
{pdf_text[:100000]}  # Truncate to avoid token limits
"""
    summary = ask_ai(prompt, model_name)
    print("Generated summary")
    return summary


def extract_paper_name(url: str) -> str:
    """Extract and format the paper name from the URL for use as filename."""
    # Get the filename from URL
    filename = url.split("/")[-1]
    # Remove .pdf extension
    name = filename.replace(".pdf", "").replace("-Paper", "")
    # Clean up the name - replace underscores with dashes, remove special chars
    name = re.sub(r'[^a-zA-Z0-9\-]', '-', name)
    # Remove multiple consecutive dashes
    name = re.sub(r'-+', '-', name)
    # Remove leading/trailing dashes
    name = name.strip('-')
    return name


def save_summary(summary: str, paper_name: str, output_dir: str = ".") -> str:
    """Save the summary as a markdown file."""
    filepath = os.path.join(output_dir, f"{paper_name}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Summary: {paper_name}\n\n")
        f.write(summary)
    print(f"Saved summary to {filepath}")
    return filepath


def summarize_paper_from_url(url: str, output_dir: str = ".", model_name: str = "gpt-4o-mini") -> str:
    """Main function: Download PDF, extract text, summarize, and save."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract paper name for filenames
    paper_name = extract_paper_name(url)
    
    # Download PDF
    pdf_path = os.path.join(output_dir, f"{paper_name}.pdf")
    download_pdf(url, pdf_path)
    
    # Extract text
    pdf_text = extract_text_from_pdf(pdf_path)
    
    # Summarize
    summary = summarize_pdf(pdf_text, model_name)
    
    # Save summary
    summary_path = save_summary(summary, paper_name, output_dir)
    
    return summary_path


# Example usage
if __name__ == "__main__":
    url = "https://proceedings.neurips.cc/paper_files/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf"
    output_dir = "./summaries"
    
    summary_path = summarize_paper_from_url(url, output_dir)
    print(f"\nDone! Summary saved to: {summary_path}")