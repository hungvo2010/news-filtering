"""
News scraper module for RSS feeds and web scraping.
Handles fetching articles from Vietnamese news sources.
"""

import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import re
import time
import feedparser
from readability import Document


def fetch_full_article_content(url: str) -> str:
    """
    Fetch and extract clean article content from URL using readability.
    
    Args:
        url: Article URL
        
    Returns:
        Clean article text content
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Set encoding to utf-8 for Vietnamese content
        response.encoding = 'utf-8'
        
        # Use readability to extract clean content
        doc = Document(response.text)  # Use .text instead of .content to avoid bytes issues
        clean_content = doc.content()
        
        # Parse HTML to get text only
        soup = BeautifulSoup(clean_content, 'html.parser')
        text_content = soup.get_text(strip=True)
        
        return text_content
    except Exception as e:
        print(f"Error fetching full content from {url}: {e}")
        return ""


def parse_rss_date(date_string: str) -> datetime:
    """
    Parse RSS date string to datetime object with +07 timezone.
    
    Args:
        date_string: Date string from RSS feed
        
    Returns:
        datetime object with timezone info
    """
    try:
        # Try parsing RFC 2822 format first
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_string)
    except (ValueError, TypeError):
        try:
            # Fallback to ISO format
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            # Return current time if parsing fails
            return datetime.now(timezone(timedelta(hours=7)))


def is_same_date(pub_date: datetime, current_date: datetime) -> bool:
    """
    Check if publication date is the same as current date (ignoring time).
    
    Args:
        pub_date: Publication datetime
        current_date: Current datetime for comparison
        
    Returns:
        True if same date, False otherwise
    """
    return pub_date.date() == current_date.date()


def format_article(raw_article: Dict[str, Any], source_name: str) -> Dict[str, str]:
    """
    Format raw article data into standardized format.
    
    Args:
        raw_article: Raw article data
        source_name: Name of the news source
        
    Returns:
        Formatted article dictionary
    """
    # Truncate summary to 150 characters
    summary = raw_article.get('description', '')
    if len(summary) > 150:
        summary = summary[:147] + '...'
    
    # Handle publish_time - convert struct_time to timezone-aware datetime
    published_parsed = raw_article.get('published_parsed')
    if published_parsed and hasattr(published_parsed, 'tm_year'):
        # Convert struct_time to datetime with Vietnam timezone
        publish_time = datetime(*published_parsed[:6], tzinfo=timezone(timedelta(hours=7)))
    else:
        # Fallback to current time with Vietnam timezone
        publish_time = datetime.now(timezone(timedelta(hours=7)))
    
    return {
        'title': raw_article.get('title', ''),
        'summary': summary,
        'url': raw_article.get('link', ''),
        'publish_time': publish_time,
        'source': source_name
    }


def fetch_rss_articles(url: str, current_date: datetime) -> List[Dict[str, str]]:
    """
    Fetch articles from RSS feed using feedparser with full content extraction.
    
    Args:
        url: RSS feed URL
        current_date: Current date for filtering
        
    Returns:
        List of article dictionaries with full content
    """
    try:
        # Use feedparser for robust RSS parsing
        feed = feedparser.parse(url)
        articles = []
        
        # Extract source name from URL
        source_name = url.split('//')[1].split('/')[0] if '//' in url else 'Unknown'
        
        for entry in feed.entries:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                # Convert struct_time to datetime with Vietnam timezone
                pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone(timedelta(hours=7)))
                
                # Only include articles from current date
                if is_same_date(pub_date, current_date):
                    # Get basic metadata
                    title = entry.get('title', '')
                    link = entry.get('link', '')
                    summary = entry.get('summary', '')[:150]
                    
                    # Fetch full content only for articles that pass basic checks
                    # Limit to first few articles to avoid too many requests
                    article_count = len(articles)
                    if article_count < 5 and link:  # Only fetch full content for first 5 articles per source
                        full_content = fetch_full_article_content(link)
                    else:
                        full_content = ''
                    
                    # Use full content for summary if available, otherwise use RSS summary
                    if full_content:
                        content_summary = full_content[:150] + '...' if len(full_content) > 150 else full_content
                    else:
                        content_summary = summary[:150] + '...' if len(summary) > 150 else summary
                    
                    article = {
                        'title': title,
                        'summary': content_summary,
                        'url': link,
                        'publish_time': pub_date,
                        'source': source_name,
                        'full_content': full_content  # Store full content for enhanced classification
                    }
                    articles.append(article)
        
        return articles[:200]  # Limit to 200 articles per source
        
    except Exception as e:
        print(f"Error fetching RSS from {url}: {e}")
        return []


def scrape_website(url: str, selectors: Dict[str, str], current_date: datetime) -> List[Dict[str, str]]:
    """
    Scrape articles from website using CSS selectors.
    
    Args:
        url: Website URL
        selectors: Dictionary with title_selector, summary_selector, date_selector
        current_date: Current date for filtering
        
    Returns:
        List of article dictionaries
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        
        # Find all article containers
        title_elements = soup.select(selectors.get('title_selector', 'h2'))
        
        source_name = url.split('//')[1].split('/')[0] if '//' in url else 'Unknown'
        
        for title_elem in title_elements[:200]:  # Limit to 200 per source
            try:
                title = title_elem.get_text(strip=True)
                
                # Try to find summary (description)
                summary_elem = title_elem.find_parent().find(selectors.get('summary_selector', '.summary'))
                summary = summary_elem.get_text(strip=True) if summary_elem else ''
                
                # Try to find link
                link_elem = title_elem.find('a') or title_elem.find_parent().find('a')
                link = link_elem.get('href') if link_elem else ''
                if link.startswith('/'):
                    link = url.rstrip('/') + link
                
                # For now, assume all scraped articles are from current date
                # In real implementation, you'd parse the date from page
                raw_article = {
                    'title': title,
                    'description': summary,
                    'link': link,
                    'published_parsed': current_date
                }
                
                articles.append(format_article(raw_article, source_name))
                
            except Exception as e:
                continue  # Skip malformed articles
        
        return articles
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []


def fetch_articles(sources: Dict[str, Any], current_date: datetime) -> List[Dict[str, str]]:
    """
    Fetch articles from multiple RSS and scraping sources.
    
    Args:
        sources: Dictionary with 'rss' and 'scraping' source lists
        current_date: Current date for filtering
        
    Returns:
        Combined list of articles from all sources
    """
    all_articles = []
    
    # Fetch from RSS sources
    for rss_url in sources.get('rss', []):
        articles = fetch_rss_articles(rss_url, current_date)
        all_articles.extend(articles)
    
    # Fetch from scraping sources
    for source_name, source_config in sources.get('scraping', {}).items():
        articles = scrape_website(
            source_config['url'],
            {
                'title_selector': source_config.get('title_selector', 'h2'),
                'summary_selector': source_config.get('summary_selector', '.summary'),
                'date_selector': source_config.get('date_selector', '.date')
            },
            current_date
        )
        all_articles.extend(articles)
    
    return all_articles