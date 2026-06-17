# /// script
# requires-python = ">=3.13"
# dependencies = [
# "requests>=2.34.1",
# "beautifulsoup4>=4.13.4"
# ]
# ///

import requests
from bs4 import BeautifulSoup

def scrape_oreilly_ai_programming_news(url):
    """
    Scrape AI and programming-related content from O'Reilly Radar.
    """
    try:
        # Send request to the website
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find AI and Programming sections
        ai_section = soup.find('h2', string=lambda text: text and 'AI' in text)
        programming_section = soup.find('h2', string=lambda text: text and 'Programming' in text)
        
        news_items = []
        
        # Extract AI content
        if ai_section:
            ai_content = ai_section.find_next('ul')
            if ai_content:
                news_items.extend([li.text.strip() for li in ai_content.find_all('li')])
        
        # Extract Programming content
        if programming_section:
            programming_content = programming_section.find_next('ul')
            if programming_content:
                news_items.extend([li.text.strip() for li in programming_content.find_all('li')])
        
        return news_items
    
    except requests.exceptions.RequestException as e:
        print(f"Error scraping website: {e}")
        return []

# Example usage (replace with actual O'Reilly Radar URL)
oreilly_url = "https://www.oreilly.com/radar/radar-trends-to-watch-january-2025/"
ai_programming_news = scrape_oreilly_ai_programming_news(oreilly_url)

if ai_programming_news:
    print("\nLatest O'Reilly AI & Programming News:")
    for idx, news in enumerate(ai_programming_news, 1):
        print(f"{idx}. {news}")