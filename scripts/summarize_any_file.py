# /// script
# requires-python = ">=3.12"
# dependencies = ["openai", "pypdf2"]
# ///

from openai import OpenAI # for accessing the model to do summarization
from PyPDF2 import PdfReader
import sys

# Load the file we want to summarize
def load_pdf_to_md(pdf_path: str):
    """
    Load the data from a pdf file and return the markdown version of the document.
    Uses PyPDF2 to extract the text and writes it to a markdown file.
    """

    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""  # Avoid None

    # Simple markdown conversion: text to "```text" code block
    md_content = f"```text\n{text}\n```"

    return md_content

def load_txt_or_md_file(file_path: str) -> str:
    """
    Loads the text or md file and returns the contents as a string.
    """
    
    with open(file_path, "r") as f:
        contents = f.read()
    
    return contents

# we need to check if this file is txt/md or pdf

def load_file_based_on_extension(file_path: str) -> str:
    """
    If the file is txt/md it will load with txt/md function
    else it will load with pdf function. 
    If its neither of those it will return an error message.
    """
    if file_path.endswith(".txt") or file_path.endswith(".md"):
        print("Loading txt/md file!")
        contents = load_txt_or_md_file(file_path)
        return contents
    elif file_path.endswith(".pdf"):
        print("Loading pdf file!")
        contents = load_pdf_to_md(file_path)
        return contents
    else:
        print("Error with loading file")
        return "File extension not accepted!"

def llm_call(prompt: str) -> str:
    """
    Receives a prompt and returns a response in text from 
    an LLM api model.
    """
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    
    text_output = response.choices[0].message.content
    
    return text_output

    
# file_path_pdf = "./paper.pdf"
# file_path_txt = "./aie-schedule.txt"
# file_path_md = "./aie-schedule.md"

file_path = sys.argv[1]
print(f"File path given as input: {file_path}")
file_contents = load_file_based_on_extension(file_path)
# print(f"File contents: {file_contents}")

# Write a prompt that uses some AI model to summarize that file
# # this variable is in all caps because its supposed to be this contant element of this script
SUMMARY_PROMPT = f"""
Summarize the following contents into compressed 
instructive bullet points:
{file_contents}
"""
# Send that prompt to an AI provider like OpenAI/Anthropic/Gemini/Ollama
output_summary = llm_call(SUMMARY_PROMPT)

# Organize the response to display to the user (it can be opening it as a markdown file, displaying it on the terminal)
print(output_summary)

