#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "requests>=2.31.0",
#     "matplotlib>=3.7.0",
#     "pillow>=10.0.0",
#     "numpy>=1.24.0"
# ]
# ///

import requests
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import numpy as np
from datetime import datetime, timedelta
import math

def fetch_nasa_images(days=9):
    """Fetch multiple NASA APOD images"""
    images = []
    base_url = "https://api.nasa.gov/planetary/apod"
    
    for i in range(days):
        # Get images from the last 'days' days
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        
        try:
            response = requests.get(
                base_url,
                params={'api_key': 'DEMO_KEY', 'date': date},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Only process if it's an image (not video)
                if data.get('media_type') == 'image':
                    img_response = requests.get(data['url'], timeout=15)
                    if img_response.status_code == 200:
                        img = Image.open(BytesIO(img_response.content))
                        # Convert to RGB if necessary
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        images.append({
                            'image': img,
                            'title': data.get('title', 'Unknown'),
                            'date': data.get('date', date),
                            'explanation': data.get('explanation', '')[:100] + '...'
                        })
                        print(f"✓ Fetched: {data.get('title', 'Unknown')}")
                    else:
                        print(f"✗ Failed to download image for {date}")
                else:
                    print(f"⚠ Skipped video content for {date}")
            else:
                print(f"✗ API request failed for {date}")
                
        except Exception as e:
            print(f"✗ Error fetching {date}: {str(e)}")
    
    return images

def create_gorgeous_grid(images):
    """Create a beautiful grid of NASA images"""
    if not images:
        print("No images to display!")
        return
    
    # Calculate grid dimensions
    n_images = len(images)
    n_cols = math.ceil(math.sqrt(n_images))
    n_rows = math.ceil(n_images / n_cols)
    
    # Create figure with dark background
    fig = plt.figure(figsize=(20, 16))
    fig.patch.set_facecolor('#0a0a0a')
    
    # Add main title
    fig.suptitle(
        '🌌 NASA Astronomy Pictures of the Day 🌌', 
        fontsize=28, 
        color='white', 
        fontweight='bold',
        y=0.95
    )
    
    for idx, img_data in enumerate(images):
        # Create subplot
        ax = plt.subplot(n_rows, n_cols, idx + 1)
        ax.set_facecolor('#1a1a1a')
        
        # Display image
        ax.imshow(np.array(img_data['image']))
        
        # Remove axes
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Add beautiful border
        for spine in ax.spines.values():
            spine.set_edgecolor('#444444')
            spine.set_linewidth(2)
        
        # Add title and date
        ax.set_title(
            f"{img_data['title']}\n{img_data['date']}", 
            fontsize=11, 
            color='white',
            fontweight='bold',
            pad=10,
            wrap=True
        )
        
        # Add subtle explanation text below image
        ax.text(
            0.5, -0.15, 
            img_data['explanation'], 
            transform=ax.transAxes, 
            fontsize=8, 
            color='#cccccc',
            ha='center',
            va='top',
            wrap=True
        )
    
    # Remove empty subplots
    for idx in range(n_images, n_rows * n_cols):
        fig.delaxes(fig.axes[idx])
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0.03, 1, 0.92])
    
    # Add footer
    fig.text(
        0.5, 0.02, 
        '🚀 Data from NASA API | Created with Python & Matplotlib 🚀', 
        ha='center', 
        fontsize=12, 
        color='#888888'
    )
    
    # Show the plot
    plt.show()
    
    # Save with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'nasa_apod_grid_{timestamp}.png'
    plt.savefig(
        filename, 
        dpi=300, 
        bbox_inches='tight', 
        facecolor='#0a0a0a',
        edgecolor='none'
    )
    print(f"\n🎨 Gorgeous grid saved as: {filename}")

def main():
    print("🌟 Fetching beautiful images from NASA...")
    print("=" * 50)
    
    # Fetch images
    images = fetch_nasa_images(days=12)  # Try to get 12 images
    
    if images:
        print(f"\n🎉 Successfully fetched {len(images)} images!")
        print("🎨 Creating gorgeous grid...")
        create_gorgeous_grid(images)
    else:
        print("😞 No images could be fetched. Please check your internet connection.")

if __name__ == "__main__":
    main()