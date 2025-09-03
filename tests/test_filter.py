"""
Unit tests for filtering functionality.
Tests negative keyword exclusion, positive keyword matching, and categorization.
"""

import sys
import os
from datetime import datetime, timezone, timedelta
import pytest

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_exclude_negative_keywords():
    """Test negative keyword exclusion functionality."""
    from filter import exclude_negative
    
    articles = [
        {
            'title': 'Công nghệ AI mới phát triển',
            'summary': 'Một công nghệ AI mới được phát triển tại Việt Nam',
            'url': 'http://test.com/1',
            'publish_time': datetime.now(),
            'source': 'test'
        },
        {
            'title': 'Tai nạn giao thông nghiêm trọng',
            'summary': 'Một vụ tai nạn giao thông xảy ra tại Hà Nội',
            'url': 'http://test.com/2',
            'publish_time': datetime.now(),
            'source': 'test'
        },
        {
            'title': 'Kinh tế Việt Nam tăng trưởng',
            'summary': 'GDP của Việt Nam tăng trưởng mạnh trong quý này',
            'url': 'http://test.com/3',
            'publish_time': datetime.now(),
            'source': 'test'
        }
    ]
    
    negative_keywords = ['tai nạn', 'thảm họa', 'giết']
    
    filtered = exclude_negative(articles, negative_keywords)
    
    # Should exclude article with "tai nạn"
    assert len(filtered) == 2
    assert 'tai nạn' not in [article['title'] for article in filtered]


def test_case_insensitive_exclusion():
    """Test that negative keyword exclusion is case-insensitive."""
    from filter import exclude_negative
    
    articles = [
        {
            'title': 'TAI NẠN giao thông',
            'summary': 'Mô tả về tai nạn',
            'url': 'http://test.com/1',
            'publish_time': datetime.now(),
            'source': 'test'
        }
    ]
    
    negative_keywords = ['tai nạn']
    
    filtered = exclude_negative(articles, negative_keywords)
    
    # Should exclude uppercase version
    assert len(filtered) == 0


def test_categorize_positive_keywords():
    """Test positive keyword matching and categorization."""
    from filter import categorize_positive
    
    articles = [
        {
            'title': 'Công nghệ AI phát triển',
            'summary': 'AI và robot được phát triển',
            'url': 'http://test.com/1',
            'publish_time': datetime.now(),
            'source': 'test'
        },
        {
            'title': 'GDP tăng trưởng mạnh',
            'summary': 'Kinh tế Việt Nam phát triển tốt',
            'url': 'http://test.com/2',
            'publish_time': datetime.now(),
            'source': 'test'
        },
        {
            'title': 'Đội tuyển bóng đá thắng lớn',
            'summary': 'Thể thao Việt Nam có thành tích tốt',
            'url': 'http://test.com/3',
            'publish_time': datetime.now(),
            'source': 'test'
        },
        {
            'title': 'Tin tức thông thường',
            'summary': 'Không có từ khóa đặc biệt',
            'url': 'http://test.com/4',
            'publish_time': datetime.now(),
            'source': 'test'
        }
    ]
    
    positive_keywords = {
        'technology': ['công nghệ', 'AI', 'robot'],
        'economy': ['kinh tế', 'GDP'],
        'sports': ['thể thao', 'bóng đá']
    }
    
    categorized = categorize_positive(articles, positive_keywords)
    
    assert 'technology' in categorized
    assert 'economy' in categorized
    assert 'sports' in categorized
    assert len(categorized['technology']) == 1
    assert len(categorized['economy']) == 1
    assert len(categorized['sports']) == 1


def test_sort_and_limit_articles():
    """Test sorting by time and limiting to top 5 articles."""
    from filter import sort_and_limit
    
    base_time = datetime(2024, 9, 3, 10, 0, 0, tzinfo=timezone(timedelta(hours=7)))
    
    categorized_articles = {
        'technology': [
            {
                'title': 'Tech 1',
                'publish_time': base_time + timedelta(hours=1),
                'summary': 'Tech summary 1',
                'url': 'http://test.com/tech1',
                'source': 'test'
            },
            {
                'title': 'Tech 2', 
                'publish_time': base_time + timedelta(hours=2),
                'summary': 'Tech summary 2',
                'url': 'http://test.com/tech2',
                'source': 'test'
            }
        ],
        'economy': [
            {
                'title': 'Econ 1',
                'publish_time': base_time + timedelta(hours=3),
                'summary': 'Econ summary 1',
                'url': 'http://test.com/econ1',
                'source': 'test'
            }
        ],
        'sports': [
            {
                'title': 'Sports 1',
                'publish_time': base_time + timedelta(hours=4),
                'summary': 'Sports summary 1',
                'url': 'http://test.com/sports1',
                'source': 'test'
            }
        ]
    }
    
    limited = sort_and_limit(categorized_articles, limit=5)
    
    assert len(limited) <= 5
    # Should be sorted by publish_time descending (newest first)
    for i in range(len(limited) - 1):
        assert limited[i]['publish_time'] >= limited[i + 1]['publish_time']


def test_filter_and_select_pipeline():
    """Test the complete filtering pipeline."""
    from filter import filter_and_select
    
    articles = [
        {
            'title': 'Tai nạn giao thông',
            'summary': 'Mô tả tai nạn',
            'url': 'http://test.com/1',
            'publish_time': datetime.now(timezone(timedelta(hours=7))),
            'source': 'test'
        },
        {
            'title': 'Công nghệ AI mới',
            'summary': 'AI phát triển mạnh',
            'url': 'http://test.com/2',
            'publish_time': datetime.now(timezone(timedelta(hours=7))),
            'source': 'test'
        }
    ]
    
    positive_keywords = {'technology': ['công nghệ', 'AI']}
    negative_keywords = ['tai nạn']
    
    result = filter_and_select(articles, positive_keywords, negative_keywords)
    
    # Should exclude negative and include positive
    assert len(result) == 1
    assert 'AI' in result[0]['title']