from openai import OpenAI
import anthropic
import ollama

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
        