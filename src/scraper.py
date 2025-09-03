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
    
    return {
        'title': raw_article.get('title', ''),
        'summary': summary,
        'url': raw_article.get('link', ''),
        'publish_time': raw_article.get('published_parsed', datetime.now(timezone(timedelta(hours=7)))),
        'source': source_name
    }


def fetch_rss_articles(url: str, current_date: datetime) -> List[Dict[str, str]]:
    """
    Fetch articles from RSS feed for current date only.
    
    Args:
        url: RSS feed URL
        current_date: Current date for filtering
        
    Returns:
        List of article dictionaries
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        articles = []
        
        # Extract source name from URL
        source_name = url.split('//')[1].split('/')[0] if '//' in url else 'Unknown'
        
        # Find all item elements
        for item in root.findall('.//item'):
            title_elem = item.find('title')
            desc_elem = item.find('description')
            link_elem = item.find('link')
            pub_date_elem = item.find('pubDate')
            
            if title_elem is not None and pub_date_elem is not None:
                pub_date = parse_rss_date(pub_date_elem.text)
                
                # Only include articles from current date
                if is_same_date(pub_date, current_date):
                    raw_article = {
                        'title': title_elem.text or '',
                        'description': desc_elem.text or '' if desc_elem is not None else '',
                        'link': link_elem.text or '' if link_elem is not None else '',
                        'published_parsed': pub_date
                    }
                    
                    articles.append(format_article(raw_article, source_name))
        
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