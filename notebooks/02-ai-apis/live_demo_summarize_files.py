# /// script
# requires-python = ">=3.12"
# dependencies = ["openai"]
# ///

# Magic inline metadata

from openai import OpenAI

def ask_ai(prompt, model_name="gpt-5-mini"):
    # access the openai API and call this model to get a response
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
    print(output)

    return output

def summarize_all_files(folder):
    import os
    summaries = []
    for entry in os.listdir(folder):
        path = os.path.join(folder, entry)
        if not os.path.isfile(path):
            continue
        if not entry.lower().endswith(('.txt', '.md')):
            continue
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            summaries.append({'filename': entry, 'error': f'Could not read file: {e}'})
            continue
        prompt = (
            f"You are a helpful assistant. Summarize the following file named '{entry}'. "
            "Provide a concise summary that captures the main points, key details, and any "
            "actions or conclusions. Keep the summary clear and brief (a few short paragraphs "
            "or bullet points). Do not include the original text.\n\n"
            "---BEGIN FILE---\n"
            f"{content}\n"
            "---END FILE---"
        )
        try:
            summary = ask_ai(prompt, model_name="gpt-5-mini")
        except Exception as e:
            summaries.append({'filename': entry, 'error': f'API error: {e}'})
            continue
        summaries.append({'filename': entry, 'summary': summary})
    return summaries

output = summarize_all_files("/Users/greatmaster/Desktop/projects/oreilly-live-trainings/oreilly-python-course")

print(output)