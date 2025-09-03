"""
Simple test script to verify basic functionality without dependency issues.
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test basic imports
print("Testing basic imports...")

try:
    from config import config
    print("✓ Config module loaded")
    
    print(f"  - SMTP Host: {config.smtp_config['host']}")
    print(f"  - Email Recipients: {len(config.email_recipients)} recipients")
    print(f"  - Positive Keywords: {list(config.positive_keywords.keys())}")
    print(f"  - RSS Sources: {len(config.rss_sources)}")
    
except Exception as e:
    print(f"✗ Config module failed: {e}")

try:
    from filter import filter_and_select, exclude_negative
    print("✓ Filter module loaded")
    
    # Test basic filtering
    sample_articles = [
        {
            'title': 'Công nghệ AI mới phát triển',
            'summary': 'AI phát triển mạnh',
            'url': 'http://test.com',
            'source': 'test',
            'publish_time': None
        }
    ]
    
    filtered = exclude_negative(sample_articles, ['tai nạn'])
    print(f"  - Negative filtering: {len(filtered)} articles remain")
    
except Exception as e:
    print(f"✗ Filter module failed: {e}")

try:
    from email_generator import generate_email_body
    from datetime import datetime, timezone, timedelta
    
    print("✓ Email generator module loaded")
    
    # Test email generation
    current_date = datetime.now(timezone(timedelta(hours=7)))
    subject, body = generate_email_body([], current_date)
    
    print(f"  - Generated subject: {subject[:50]}...")
    print(f"  - Body length: {len(body)} characters")
    print(f"  - Contains HTML: {'<html' in body}")
    
except Exception as e:
    print(f"✗ Email generator failed: {e}")

print("\nBasic functionality test completed!")
print("\nTo run full tests:")
print("  python3 -c 'import sys; sys.path.insert(0, \"src\"); from config import *; print(\"All imports successful!\")'")