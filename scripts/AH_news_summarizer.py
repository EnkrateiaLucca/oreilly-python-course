#!/usr/bin/env python3
# /// script
# dependencies = ["requests", "beautifulsoup4", "anthropic", "python-dotenv", "feedparser", "newspaper3k"]
# ///

"""
AH_news_summarizer.py
Student: AH - "Collect news from internet and create summary for that"

This script demonstrates automated news collection from various sources,
content extraction, and AI-powered summarization for daily news briefings.

Key Learning Objectives:
- Web scraping and RSS feed parsing
- Content extraction and cleaning
- AI-powered text summarization
- Multi-source news aggregation
- Automated reporting and alerting
"""

import os
import re
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv
import anthropic

# News processing libraries
import feedparser
from bs4 import BeautifulSoup
from newspaper import Article

# Load environment variables
load_dotenv()

class NewsCollector:
    """
    A class to collect news from various sources including RSS feeds,
    news websites, and APIs, then summarize using AI.
    """

    def __init__(self):
        """Initialize the news collector with AI client and news sources."""
        # Initialize Anthropic client for AI-powered summarization
        self.ai_client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )

        # Define news sources (RSS feeds and websites)
        self.news_sources = {
            "technology": {
                "rss_feeds": [
                    "https://feeds.feedburner.com/oreilly/radar",
                    "https://techcrunch.com/feed/",
                    "https://www.wired.com/feed/rss",
                    "https://www.theverge.com/rss/index.xml"
                ],
                "websites": [
                    "https://news.ycombinator.com/",
                    "https://www.reddit.com/r/technology.json"
                ]
            },
            "business": {
                "rss_feeds": [
                    "https://feeds.bloomberg.com/markets/news.rss",
                    "https://www.reuters.com/technology/feed/",
                    "https://www.forbes.com/innovation/feed/"
                ]
            },
            "science": {
                "rss_feeds": [
                    "https://www.sciencedaily.com/rss/all.xml",
                    "https://www.nature.com/subjects/biological-sciences.rss"
                ]
            },
            "general": {
                "rss_feeds": [
                    "https://rss.cnn.com/rss/edition.rss",
                    "https://feeds.nbcnews.com/nbcnews/public/news"
                ]
            }
        }

        # News categories for classification
        self.categories = [
            "technology", "business", "science", "politics", "health",
            "entertainment", "sports", "world_news", "local_news"
        ]

        # Initialize session for HTTP requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def collect_rss_news(self, category: str, max_articles: int = 10) -> List[Dict[str, Any]]:
        """
        Collect news articles from RSS feeds for a specific category.

        Args:
            category: News category to collect
            max_articles: Maximum number of articles to collect per feed

        Returns:
            List of news article dictionaries
        """

        print(f"📡 Collecting RSS news for category: {category}")

        articles = []
        rss_feeds = self.news_sources.get(category, {}).get("rss_feeds", [])

        for feed_url in rss_feeds:
            try:
                print(f"  📰 Fetching from: {urlparse(feed_url).netloc}")

                # Parse RSS feed
                feed = feedparser.parse(feed_url)

                if feed.bozo:
                    print(f"    ⚠️ Warning: Feed may have issues")

                # Extract articles from feed
                for entry in feed.entries[:max_articles]:
                    article = {
                        "title": entry.get("title", "No title"),
                        "url": entry.get("link", ""),
                        "description": entry.get("description", ""),
                        "published": entry.get("published", ""),
                        "source": feed.feed.get("title", urlparse(feed_url).netloc),
                        "category": category,
                        "collection_method": "rss",
                        "content": "",  # Will be filled by content extraction
                        "summary": ""   # Will be filled by AI summarization
                    }

                    # Clean description from HTML tags
                    if article["description"]:
                        soup = BeautifulSoup(article["description"], 'html.parser')
                        article["description"] = soup.get_text().strip()

                    articles.append(article)

            except Exception as e:
                print(f"    ❌ Error fetching from {feed_url}: {str(e)}")

        print(f"  ✅ Collected {len(articles)} articles from RSS feeds")
        return articles

    def extract_article_content(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract full content from a news article URL.

        Args:
            article: Article dictionary with URL

        Returns:
            Article dictionary with extracted content
        """

        try:
            # Use newspaper3k for content extraction
            news_article = Article(article["url"])
            news_article.download()
            news_article.parse()

            # Update article with extracted content
            article["content"] = news_article.text
            article["authors"] = news_article.authors
            article["publish_date"] = news_article.publish_date.isoformat() if news_article.publish_date else ""
            article["top_image"] = news_article.top_image
            article["keywords"] = news_article.keywords

            # Fallback to description if content is too short
            if len(article["content"]) < 100:
                article["content"] = article["description"]

        except Exception as e:
            print(f"    ⚠️ Content extraction failed for {article['title'][:50]}...: {str(e)}")
            # Use description as fallback content
            article["content"] = article["description"]

        return article

    def collect_from_website(self, website_url: str, category: str) -> List[Dict[str, Any]]:
        """
        Collect news from a specific website by scraping.

        Args:
            website_url: URL of the website to scrape
            category: Category to assign to collected articles

        Returns:
            List of news article dictionaries
        """

        articles = []

        try:
            print(f"  🌐 Scraping website: {urlparse(website_url).netloc}")

            response = self.session.get(website_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Special handling for different websites
            if "news.ycombinator.com" in website_url:
                articles = self._scrape_hackernews(soup, category)
            elif "reddit.com" in website_url:
                articles = self._scrape_reddit_json(website_url, category)
            else:
                # Generic article extraction
                articles = self._scrape_generic_news(soup, website_url, category)

        except Exception as e:
            print(f"    ❌ Error scraping {website_url}: {str(e)}")

        return articles

    def _scrape_hackernews(self, soup: BeautifulSoup, category: str) -> List[Dict[str, Any]]:
        """Scrape articles from Hacker News."""
        articles = []

        # Find article titles and links
        title_links = soup.find_all('a', class_='storylink')[:10]  # Top 10 articles

        for link in title_links:
            article = {
                "title": link.get_text().strip(),
                "url": link.get('href', ''),
                "description": "",
                "published": datetime.now().isoformat(),
                "source": "Hacker News",
                "category": category,
                "collection_method": "web_scraping",
                "content": "",
                "summary": ""
            }

            # Make URL absolute if relative
            if article["url"].startswith('item?'):
                article["url"] = f"https://news.ycombinator.com/{article['url']}"
            elif not article["url"].startswith('http'):
                article["url"] = f"https://news.ycombinator.com/{article['url']}"

            articles.append(article)

        return articles

    def _scrape_reddit_json(self, url: str, category: str) -> List[Dict[str, Any]]:
        """Scrape articles from Reddit JSON API."""
        articles = []

        try:
            response = self.session.get(url, timeout=10)
            data = response.json()

            for post in data['data']['children'][:10]:  # Top 10 posts
                post_data = post['data']

                article = {
                    "title": post_data.get('title', ''),
                    "url": post_data.get('url', ''),
                    "description": post_data.get('selftext', '')[:500],  # Limit description
                    "published": datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat(),
                    "source": f"Reddit r/{post_data.get('subreddit', 'unknown')}",
                    "category": category,
                    "collection_method": "api",
                    "content": post_data.get('selftext', ''),
                    "summary": "",
                    "score": post_data.get('score', 0),
                    "comments": post_data.get('num_comments', 0)
                }

                articles.append(article)

        except Exception as e:
            print(f"    ❌ Error parsing Reddit JSON: {str(e)}")

        return articles

    def _scrape_generic_news(self, soup: BeautifulSoup, base_url: str, category: str) -> List[Dict[str, Any]]:
        """Generic news website scraping."""
        articles = []

        # Common selectors for news articles
        article_selectors = [
            'article h2 a', 'h2 a', 'h3 a', '.article-title a',
            '.headline a', '.story-headline a', '.entry-title a'
        ]

        for selector in article_selectors:
            links = soup.select(selector)[:10]  # Limit to 10 articles

            for link in links:
                href = link.get('href', '')
                if href:
                    # Make URL absolute
                    full_url = urljoin(base_url, href)

                    article = {
                        "title": link.get_text().strip(),
                        "url": full_url,
                        "description": "",
                        "published": datetime.now().isoformat(),
                        "source": urlparse(base_url).netloc,
                        "category": category,
                        "collection_method": "web_scraping",
                        "content": "",
                        "summary": ""
                    }

                    articles.append(article)

            if articles:  # If we found articles, no need to try other selectors
                break

        return articles

    def summarize_articles_with_ai(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Use AI to summarize individual articles and create topic summaries.

        Args:
            articles: List of articles to summarize

        Returns:
            List of articles with AI-generated summaries
        """

        print("🤖 Generating AI summaries for articles...")

        summarized_articles = []

        for i, article in enumerate(articles):
            try:
                print(f"  📝 Summarizing article {i+1}/{len(articles)}: {article['title'][:50]}...")

                # Prepare content for summarization
                content_to_summarize = article["content"] or article["description"]

                if len(content_to_summarize) < 50:
                    # Skip very short articles
                    article["summary"] = "Article content too short for meaningful summary."
                    article["key_points"] = []
                    article["sentiment"] = "neutral"
                    summarized_articles.append(article)
                    continue

                # Create AI prompt for article summarization
                prompt = f"""
                Summarize this news article and provide key insights:

                Title: {article['title']}
                Source: {article['source']}
                Content: {content_to_summarize[:2000]}  # Limit content length

                Provide:
                1. A concise 2-3 sentence summary
                2. 3-5 key points or takeaways
                3. Overall sentiment (positive, negative, neutral)
                4. Relevance category from: {', '.join(self.categories)}

                Respond in JSON format:
                {{
                    "summary": "concise summary",
                    "key_points": ["point1", "point2", "point3"],
                    "sentiment": "positive/negative/neutral",
                    "category": "category",
                    "importance_score": 1-10
                }}
                """

                # Make API call to Anthropic
                response = self.ai_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )

                # Parse AI response
                ai_summary = json.loads(response.content[0].text)

                # Update article with AI-generated content
                article["summary"] = ai_summary.get("summary", "Summary not available")
                article["key_points"] = ai_summary.get("key_points", [])
                article["sentiment"] = ai_summary.get("sentiment", "neutral")
                article["ai_category"] = ai_summary.get("category", article["category"])
                article["importance_score"] = ai_summary.get("importance_score", 5)

            except Exception as e:
                print(f"    ❌ Summarization failed for {article['title'][:50]}...: {str(e)}")
                # Fallback summary
                article["summary"] = "AI summarization unavailable. " + article["description"][:200]
                article["key_points"] = ["Content analysis pending"]
                article["sentiment"] = "neutral"
                article["importance_score"] = 5

            summarized_articles.append(article)

        print(f"  ✅ Completed summarization for {len(summarized_articles)} articles")
        return summarized_articles

    def create_daily_briefing(self, articles: List[Dict[str, Any]]) -> str:
        """
        Create a comprehensive daily news briefing from collected articles.

        Args:
            articles: List of summarized articles

        Returns:
            Formatted daily briefing text
        """

        print("📊 Creating daily news briefing...")

        # Sort articles by importance score
        sorted_articles = sorted(articles, key=lambda x: x.get("importance_score", 5), reverse=True)

        # Group articles by category
        articles_by_category = {}
        for article in sorted_articles:
            category = article.get("ai_category", article["category"])
            if category not in articles_by_category:
                articles_by_category[category] = []
            articles_by_category[category].append(article)

        # Generate briefing
        briefing = []
        briefing.append("=" * 80)
        briefing.append("📰 DAILY NEWS BRIEFING")
        briefing.append("=" * 80)
        briefing.append(f"Generated: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}")
        briefing.append(f"Total articles analyzed: {len(articles)}")
        briefing.append("")

        # Executive summary
        briefing.append("🎯 EXECUTIVE SUMMARY:")
        briefing.append("-" * 30)

        # Get top 3 most important articles
        top_articles = sorted_articles[:3]
        for i, article in enumerate(top_articles, 1):
            briefing.append(f"{i}. {article['title']}")
            briefing.append(f"   {article['summary']}")
            briefing.append(f"   Source: {article['source']} | Importance: {article.get('importance_score', 5)}/10")
            briefing.append("")

        # Category breakdown
        briefing.append("📂 NEWS BY CATEGORY:")
        briefing.append("-" * 25)

        for category, cat_articles in articles_by_category.items():
            if not cat_articles:
                continue

            briefing.append(f"\n🔸 {category.upper().replace('_', ' ')} ({len(cat_articles)} articles)")
            briefing.append("-" * 40)

            # Show top 3 articles per category
            for article in cat_articles[:3]:
                briefing.append(f"• {article['title']}")
                briefing.append(f"  {article['summary']}")
                briefing.append(f"  Source: {article['source']} | Sentiment: {article.get('sentiment', 'neutral')}")

                # Show key points
                key_points = article.get("key_points", [])
                if key_points:
                    briefing.append("  Key Points:")
                    for point in key_points[:2]:  # Show top 2 points
                        briefing.append(f"    - {point}")
                briefing.append("")

        # Sentiment analysis
        sentiments = [article.get("sentiment", "neutral") for article in articles]
        sentiment_counts = {
            "positive": sentiments.count("positive"),
            "negative": sentiments.count("negative"),
            "neutral": sentiments.count("neutral")
        }

        briefing.append("📈 SENTIMENT ANALYSIS:")
        briefing.append("-" * 25)
        for sentiment, count in sentiment_counts.items():
            percentage = (count / len(articles)) * 100 if articles else 0
            briefing.append(f"{sentiment.capitalize()}: {count} articles ({percentage:.1f}%)")
        briefing.append("")

        # Sources summary
        sources = [article["source"] for article in articles]
        source_counts = {}
        for source in sources:
            source_counts[source] = source_counts.get(source, 0) + 1

        briefing.append("📡 TOP NEWS SOURCES:")
        briefing.append("-" * 25)
        sorted_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)
        for source, count in sorted_sources[:5]:
            briefing.append(f"{source}: {count} articles")
        briefing.append("")

        # Trending topics (most common keywords)
        all_keywords = []
        for article in articles:
            keywords = article.get("keywords", [])
            if isinstance(keywords, list):
                all_keywords.extend(keywords)

        if all_keywords:
            keyword_counts = {}
            for keyword in all_keywords:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1

            briefing.append("🔥 TRENDING TOPICS:")
            briefing.append("-" * 20)
            sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
            for keyword, count in sorted_keywords[:10]:
                briefing.append(f"{keyword}: {count} mentions")
            briefing.append("")

        # Action items and recommendations
        briefing.append("📋 RECOMMENDED ACTIONS:")
        briefing.append("-" * 30)
        briefing.append("• Monitor high-importance articles for follow-up")
        briefing.append("• Track sentiment trends in your industry")
        briefing.append("• Review negative sentiment articles for potential impact")
        briefing.append("• Consider amplifying positive news related to your sector")
        briefing.append("")

        briefing.append("🔗 This briefing was generated automatically using AI-powered news analysis.")

        return "\n".join(briefing)

    def collect_all_news(self, categories: List[str] = None) -> List[Dict[str, Any]]:
        """
        Collect news from all configured sources across specified categories.

        Args:
            categories: List of categories to collect (default: all)

        Returns:
            List of all collected articles
        """

        if categories is None:
            categories = list(self.news_sources.keys())

        all_articles = []

        print("🚀 Starting comprehensive news collection...")

        for category in categories:
            print(f"\n📂 Processing category: {category}")

            # Collect from RSS feeds
            rss_articles = self.collect_rss_news(category, max_articles=5)
            all_articles.extend(rss_articles)

            # Collect from websites
            websites = self.news_sources.get(category, {}).get("websites", [])
            for website in websites:
                try:
                    website_articles = self.collect_from_website(website, category)
                    all_articles.extend(website_articles)
                except Exception as e:
                    print(f"    ❌ Website collection failed: {str(e)}")

        print(f"\n📊 Total articles collected: {len(all_articles)}")

        # Extract content for articles that don't have it
        print("📄 Extracting article content...")
        for i, article in enumerate(all_articles):
            if not article.get("content") and article.get("url"):
                print(f"  📝 Extracting content {i+1}/{len(all_articles)}")
                article = self.extract_article_content(article)

        return all_articles

def main():
    """
    Main function to demonstrate news collection and summarization.
    """

    print("🚀 News Summarizer Demo")
    print("=" * 40)

    # Initialize the news collector
    collector = NewsCollector()

    # Collect news from multiple sources
    print("📡 Collecting news from various sources...")
    all_articles = collector.collect_all_news(categories=["technology", "business"])

    if not all_articles:
        print("❌ No articles collected. Check your internet connection and news sources.")
        return

    print(f"✅ Collected {len(all_articles)} articles")

    # Generate AI summaries
    print("\n🤖 Generating AI-powered summaries...")
    summarized_articles = collector.summarize_articles_with_ai(all_articles[:10])  # Limit for demo

    # Create daily briefing
    print("\n📊 Creating daily news briefing...")
    briefing = collector.create_daily_briefing(summarized_articles)

    # Display briefing
    print("\n" + briefing)

    # Save results
    output_file = f"news_briefing_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(briefing)

    # Save raw data
    json_file = f"news_data_{datetime.now().strftime('%Y%m%d')}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(summarized_articles, f, indent=2, default=str, ensure_ascii=False)

    print(f"\n💾 Briefing saved to: {output_file}")
    print(f"💾 Raw data saved to: {json_file}")

    # Demonstrate integration possibilities
    print("\n🔗 INTEGRATION POSSIBILITIES:")
    print("- Scheduled daily/hourly news collection")
    print("- Email/Slack notifications for breaking news")
    print("- RSS feed generation for custom topics")
    print("- Integration with content management systems")
    print("- Social media monitoring and analysis")
    print("- Competitor news tracking")
    print("- Industry-specific news filtering")
    print("- Multi-language news collection and translation")
    print("- Real-time news alerts based on keywords")
    print("- News trend analysis and reporting")

if __name__ == "__main__":
    main()