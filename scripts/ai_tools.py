# PACKAGES 
from openai import OpenAI
import anthropic
import ollama
import json


# CODE (SCRIPT!)
def ask_ai(prompt, model_name="gpt-4o-mini"):
    """
    Send prompt to an LLM and get output text back.    
    """
    if "claude" in model_name:
        client = anthropic.Anthropic()

        # Send a message to the Claude AI
        response = client.messages.create(
            model=model_name,
            messages=[
                {
                    "role": "user", "content": prompt
                }
                ],
            max_tokens=4000,
        )
        output = response.content[0].text
        return output        
    else:
        client = OpenAI()
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )
        output = response.choices[0].message.content
        return output


def ask_local_ai(prompt, model_name="llama3.2", structured=False):
    """
    Send prompt to a local LLM and get output text back.
    """
    client = ollama.Client()
    if structured:
        response = client.chat(model=model_name, 
                               messages=
                               [
                                   {"role": "user", "content": prompt}
                                ],
                               format='json')
        return response.message.content
    else:
        response = client.chat(model=model_name, 
                               messages=
                               [
                                   {"role": "user", "content": prompt}
                                ])
        return response.message.content


def parse_dates_list(output_str):
    """
    Parse the string output containing a Python list of dates into an actual Python list.
    
    Args:
        output_str (str): String containing a Python list representation of dates
        
    Returns:
        list: List of date strings
    """
    # Remove markdown code block formatting if present
    output_str = output_str.replace('```python', '').replace('```', '').strip()
    
    # Safely evaluate the string as a Python expression
    dates_list = eval(output_str)
    
    return dates_list

def parse_json_output(json_str):
    """
    This function parses the JSON output from the AI and removes the markdown code block markers if present.
    """
    # Remove markdown code block markers if present
    json_str = json_str.replace('```json', '').replace('```', '').strip()
    
    # Parse the JSON string into a Python dictionary
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        print("Error: Could not parse JSON string")
        return None