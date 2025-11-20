# /// script
# requires-python = ">=3.12"
# dependencies = ["openai"]
# ///

# Above is INLINE METADATA FOR RUNNING STANDALONE UV SCRIPTS

from openai import OpenAI

client = OpenAI()

# We will create a function that can summarize a text file in bullet points using gpt-5-mini

def summarize_with_ai(text_file_contents):
    response = client.responses.create(
        model="gpt-5-mini",
        input=f"Summarize in bullet points, this file: {text_file_contents}"
    )
    
    return response.output_text

def read_file(file_path):
    with open(file_path, "r") as f:
        contents = f.read()
    
    return contents

file_path = "/Users/greatmaster/Desktop/projects/oreilly-live-trainings/oreilly-python-course/scripts/ai_tools.py"

contents = read_file(file_path)

summary = summarize_with_ai(contents)

print("SUMMARY OUTPUT:")

print(summary)

print("###############")