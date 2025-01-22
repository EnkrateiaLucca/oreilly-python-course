from openai import OpenAI

client = OpenAI()

def ask_ai(prompt):
    """
    Send prompt to an LLM and get output text back.    
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful programming assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )
    
    return response.choices[0].message.content


