"""
Unit tests for RSS scraper functionality.
"""

import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone, timedelta
import pytest
import responses

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_fetch_rss_articles_mock():
    """Test RSS article fetching with mocked response."""
    from scraper import fetch_rss_articles
    
    # Mock RSS feed content
    mock_rss_content = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>Test News</title>
            <item>
                <title>Test Article 1</title>
                <description>This is test article 1 summary</description>
                <link>http://test.com/article1</link>
                <pubDate>Tue, 03 Sep 2024 10:00:00 +0700</pubDate>
            </item>
            <item>
                <title>Test Article 2</title>
                <description>This is test article 2 summary</description>
                <link>http://test.com/article2</link>
                <pubDate>Tue, 02 Sep 2024 10:00:00 +0700</pubDate>
            </item>
        </channel>
    </rss>"""
    
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, 'http://test.com/rss', body=mock_rss_content, status=200)
        
        current_date = datetime(2024, 9, 3, tzinfo=timezone(timedelta(hours=7)))
        articles = fetch_rss_articles('http://test.com/rss', current_date)
        
        # Should only return articles from current date
        assert len(articles) == 1
        assert articles[0]['title'] == 'Test Article 1'
        assert 'summary' in articles[0]
        assert 'url' in articles[0]
        assert 'source' in articles[0]


def test_date_filtering():
    """Test that articles are filtered by current date."""
    from scraper import is_same_date
    
    # Test timezone-aware date comparison
    current_date = datetime(2024, 9, 3, tzinfo=timezone(timedelta(hours=7)))
    
    # Same date
    pub_date1 = datetime(2024, 9, 3, 15, 30, tzinfo=timezone(timedelta(hours=7)))
    assert is_same_date(pub_date1, current_date) == True
    
    # Different date
    pub_date2 = datetime(2024, 9, 2, 15, 30, tzinfo=timezone(timedelta(hours=7)))
    assert is_same_date(pub_date2, current_date) == False


def test_article_format():
    """Test that articles are formatted correctly."""
    from scraper import format_article
    
    raw_article = {
        'title': 'Very long article title that should be truncated if it exceeds the maximum length allowed for summaries',
        'description': 'This is a very long description that should be truncated to 150 characters maximum to fit in the email format requirements',
        'link': 'http://test.com/article',
        'published_parsed': datetime(2024, 9, 3, 15, 30, tzinfo=timezone(timedelta(hours=7)))
    }
    
    formatted = format_article(raw_article, 'test_source')
    
    assert 'title' in formatted
    assert 'summary' in formatted
    assert 'url' in formatted
    assert 'publish_time' in formatted
    assert 'source' in formatted
    assert len(formatted['summary']) <= 150
    assert formatted['source'] == 'test_source'