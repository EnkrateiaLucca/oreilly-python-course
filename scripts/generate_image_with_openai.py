# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "openai",
#   "pillow",
# ]
# ///

import base64
import io
import sys
from datetime import datetime
from pathlib import Path

from openai import OpenAI
from PIL import Image


def generate_image(prompt: str) -> bytes:
    """Generate an image using OpenAI's API and return the image bytes."""
    client = OpenAI()
    
    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        n=1,
        size="1024x1024",
    )
    
    image_bytes = base64.b64decode(response.data[0].b64_json)
    return image_bytes


def display_image(image_bytes: bytes) -> Image.Image:
    """Display the image and return the PIL Image object."""
    image = Image.open(io.BytesIO(image_bytes))
    image.show()
    return image


def save_image(image_bytes: bytes, prompt: str) -> Path:
    """Save the image locally with a timestamped filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_prompt = "".join(c if c.isalnum() or c in " -_" else "" for c in prompt[:30]).strip()
    safe_prompt = safe_prompt.replace(" ", "_")
    filename = f"{timestamp}_{safe_prompt}.png"
    
    filepath = Path(filename)
    filepath.write_bytes(image_bytes)
    return filepath


def main():
    prompt = input("Enter your image prompt: ").strip()
    
    if not prompt:
        print("Error: Prompt cannot be empty.")
        sys.exit(1)
    
    print(f"\nGenerating image for: '{prompt}'...")
    
    try:
        image_bytes = generate_image(prompt)
    except Exception as e:
        print(f"Error generating image: {e}")
        sys.exit(1)
    
    print("Image generated. Displaying...")
    display_image(image_bytes)
    
    while True:
        response = input("\nApprove and save this image? (yes/no): ").strip().lower()
        if response in ("yes", "y"):
            filepath = save_image(image_bytes, prompt)
            print(f"Image saved to: {filepath.absolute()}")
            break
        elif response in ("no", "n"):
            print("Image discarded.")
            break
        else:
            print("Please enter 'yes' or 'no'.")


if __name__ == "__main__":
    main()