"""
Unit tests for email generation functionality.
"""

import sys
import os
from datetime import datetime, timezone, timedelta
import pytest

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_generate_email_body_with_articles():
    """Test email body generation with articles."""
    from email_generator import generate_email_body
    
    articles = [
        {
            'title': 'Công nghệ AI phát triển mạnh',
            'summary': 'Công nghệ trí tuệ nhân tạo đang phát triển với tốc độ nhanh chóng tại Việt Nam.',
            'url': 'http://test.com/ai-news',
            'publish_time': datetime(2024, 9, 3, 15, 30, tzinfo=timezone(timedelta(hours=7))),
            'source': 'vnexpress.net'
        },
        {
            'title': 'Kinh tế Việt Nam tăng trưởng',
            'summary': 'GDP của Việt Nam trong quý III đạt mức tăng trưởng ấn tượng.',
            'url': 'http://test.com/economy-news',
            'publish_time': datetime(2024, 9, 3, 14, 15, tzinfo=timezone(timedelta(hours=7))),
            'source': 'tuoitre.vn'
        }
    ]
    
    current_date = datetime(2024, 9, 3, tzinfo=timezone(timedelta(hours=7)))
    
    subject, body = generate_email_body(articles, current_date)
    
    # Check subject
    assert 'Bản tin tóm tắt' in subject
    assert '03/09/2024' in subject
    
    # Check body structure
    assert 'Xin chào' in body
    assert 'tin tức nổi bật' in body
    assert 'Công nghệ AI phát triển mạnh' in body
    assert 'Kinh tế Việt Nam tăng trưởng' in body
    assert 'vnexpress.net' in body
    assert 'tuoitre.vn' in body
    assert 'http://test.com/ai-news' in body
    assert 'Chúc bạn có một ngày tốt lành' in body


def test_generate_email_body_no_articles():
    """Test email body generation with no articles (fallback case)."""
    from email_generator import generate_email_body
    
    articles = []
    current_date = datetime(2024, 9, 3, tzinfo=timezone(timedelta(hours=7)))
    
    subject, body = generate_email_body(articles, current_date)
    
    # Check fallback content
    assert 'Bản tin tóm tắt' in subject
    assert '03/09/2024' in subject
    assert 'Không có tin tức phù hợp hôm nay' in body
    assert 'Chúc bạn có một ngày tốt lành' in body


def test_truncate_summary():
    """Test that long summaries are properly truncated."""
    from email_generator import generate_email_body
    
    long_summary = 'Đây là một bản tóm tắt rất dài ' * 10  # Create very long summary
    
    articles = [
        {
            'title': 'Test Article',
            'summary': long_summary,
            'url': 'http://test.com/1',
            'publish_time': datetime.now(timezone(timedelta(hours=7))),
            'source': 'test.com'
        }
    ]
    
    current_date = datetime.now(timezone(timedelta(hours=7)))
    subject, body = generate_email_body(articles, current_date)
    
    # Check that summary is truncated (should end with ...)
    lines = body.split('\n')
    summary_line = next((line for line in lines if long_summary[:50] in line), None)
    assert summary_line is not None
    # The line should be reasonably short (less than 200 chars)
    assert len(summary_line) < 200


def test_html_formatting():
    """Test that email contains proper HTML formatting."""
    from email_generator import generate_email_body
    
    articles = [
        {
            'title': 'Test Article',
            'summary': 'Test summary',
            'url': 'http://test.com/1',
            'publish_time': datetime.now(timezone(timedelta(hours=7))),
            'source': 'test.com'
        }
    ]
    
    current_date = datetime.now(timezone(timedelta(hours=7)))
    subject, body = generate_email_body(articles, current_date)
    
    # Check for basic HTML structure
    assert '<html' in body
    assert '<body>' in body
    assert '</html>' in body
    assert '</body>' in body
    assert '<h1>' in body or '<h2>' in body  # Headers
    assert '<a href=' in body  # Links
    assert '<div' in body or '<p>' in body  # Content containers


def test_responsive_email_design():
    """Test that email includes responsive design elements."""
    from email_generator import generate_email_body
    
    articles = [
        {
            'title': 'Test Article',
            'summary': 'Test summary',
            'url': 'http://test.com/1',
            'publish_time': datetime.now(timezone(timedelta(hours=7))),
            'source': 'test.com'
        }
    ]
    
    current_date = datetime.now(timezone(timedelta(hours=7)))
    subject, body = generate_email_body(articles, current_date)
    
    # Check for responsive design elements
    assert 'max-width' in body.lower()  # Responsive width
    assert 'mobile' in body.lower() or '@media' in body.lower()  # Mobile responsiveness