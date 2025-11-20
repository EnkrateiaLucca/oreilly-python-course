# /// script
# requires-python = ">=3.12"
# dependencies = ["openai", "dotenv"]
# ///

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

api_key_openai = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key_openai)

response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[
        {"role": "user", "content": "Explain best practices for beginners on running python scripts safely with uv."}
    ]
)

print(response.choices[0].message.content)