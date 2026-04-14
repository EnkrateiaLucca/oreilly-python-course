# /// script
# requires-python=">=3.12"
# dependencies=["openai","pydantic"]
# ///

from pydantic import BaseModel, Field
from openai import OpenAI
import sys

def load_receipt_data(file_path: str):
    with open(file_path, "r") as f:
        receipt_data = f.read()
    
    return receipt_data

class ReceiptData(BaseModel):
    company_name: str = Field(description="The name of the company.")
    date_of_closure: str = Field(description="The date of closure.")
    amount_paid: float = Field(description="The amount paid ('Total Pago') after taxes.")

client = OpenAI()

file_path = sys.argv[1]
receipt_data = load_receipt_data(file_path)
completion = client.beta.chat.completions.parse(
    model="gpt-5-mini",
    messages=[
        {"role": "system", "content": """
         You are an extraction engine for receipt data.
         Users will upload the contents of their receipts and you will extract
         the following fields:
         - Company name
         - Date of closure
         - Amount paid
         """},
        {"role": "user", "content": receipt_data},
    ],
    response_format=ReceiptData,
)

message = completion.choices[0].message
if message.parsed:
    print(message.parsed)
else:
    print(message.refusal)