"""
Enhanced tests for the filter module.
Tests Vietnamese text processing, deduplication, and comprehensive filtering logic.
"""

from datetime import datetime, timezone, timedelta
from src.filter import (
    preprocess_vietnamese_text,
    check_keyword_match,
    exclude_negative,
    categorize_positive,
    sort_and_limit,
    filter_and_select
)


class TestVietnameseTextProcessing:
    """Test Vietnamese text preprocessing and keyword matching."""
    
    def test_preprocess_vietnamese_text_basic(self):
        """Test basic text preprocessing."""
        text = "Công Nghệ AI Và Robot"
        result = preprocess_vietnamese_text(text)
        assert result == "công nghệ ai và robot"
    
    def test_preprocess_vietnamese_text_empty(self):
        """Test preprocessing with empty text."""
        result = preprocess_vietnamese_text("")
        assert result == ""
        
        result = preprocess_vietnamese_text(None)
        assert result == ""
    
    def test_check_keyword_match_basic(self):
        """Test basic keyword matching."""
        text = "Tin tức về công nghệ AI mới nhất"
        keywords = ["công nghệ", "robot"]
        assert check_keyword_match(text, keywords) is True
        
        keywords = ["thể thao", "bóng đá"]
        assert check_keyword_match(text, keywords) is False
    
    def test_check_keyword_match_case_insensitive(self):
        """Test case-insensitive keyword matching."""
        text = "CÔNG NGHỆ AI"
        keywords = ["công nghệ"]
        assert check_keyword_match(text, keywords) is True
    
    def test_check_keyword_match_empty_inputs(self):
        """Test keyword matching with empty inputs."""
        assert check_keyword_match("", ["test"]) is False
        assert check_keyword_match("test", []) is False
        assert check_keyword_match("", []) is False


class TestNegativeFiltering:
    """Test negative keyword exclusion."""
    
    def test_exclude_negative_basic(self):
        """Test basic negative filtering."""
        articles = [
            {
                'title': 'Tin tức công nghệ mới',
                'summary': 'Thông tin về AI và robot',
                'url': 'http://example.com/1'
            },
            {
                'title': 'Tai nạn giao thông nghiêm trọng',
                'summary': 'Vụ tai nạn làm nhiều người chết',
                'url': 'http://example.com/2'
            }
        ]
        
        negative_keywords = ['tai nạn', 'chết']
        result = exclude_negative(articles, negative_keywords)
        
        assert len(result) == 1
        assert result[0]['title'] == 'Tin tức công nghệ mới'
    
    def test_exclude_negative_empty_keywords(self):
        """Test negative filtering with empty keywords."""
        articles = [{'title': 'Test article', 'summary': 'Test summary'}]
        result = exclude_negative(articles, [])
        assert len(result) == 1
    
    def test_exclude_negative_violence_keywords(self):
        """Test filtering of violence-related content."""
        articles = [
            {
                'title': 'Nữ sinh bị đánh hội đồng',
                'summary': 'Học sinh bị túm tóc và đấm đá',
                'url': 'http://example.com/violence'
            },
            {
                'title': 'Tin tức kinh tế',
                'summary': 'GDP tăng trưởng tích cực',
                'url': 'http://example.com/economy'
            }
        ]
        
        negative_keywords = ['đánh', 'túm tóc', 'đấm đá', 'hội đồng']
        result = exclude_negative(articles, negative_keywords)
        
        assert len(result) == 1
        assert 'kinh tế' in result[0]['title']


class TestPositiveCategorization:
    """Test positive keyword categorization."""
    
    def test_categorize_positive_basic(self):
        """Test basic positive categorization."""
        articles = [
            {
                'title': 'Công nghệ AI mới',
                'summary': 'Robot thông minh',
                'full_content': 'Nội dung về trí tuệ nhân tạo',
                'url': 'http://example.com/tech'
            },
            {
                'title': 'Tăng trưởng kinh tế',
                'summary': 'GDP tăng mạnh',
                'full_content': 'Nội dung về đầu tư và phát triển',
                'url': 'http://example.com/economy'
            }
        ]
        
        positive_keywords = {
            'technology': ['công nghệ', 'AI', 'robot'],
            'economy': ['kinh tế', 'GDP', 'đầu tư']
        }
        
        result = categorize_positive(articles, positive_keywords)
        
        assert 'technology' in result
        assert 'economy' in result
        assert len(result['technology']) == 1
        assert len(result['economy']) == 1
    
    def test_categorize_positive_full_content_matching(self):
        """Test categorization using full content."""
        articles = [
            {
                'title': 'Tin tức mới',
                'summary': 'Thông tin cập nhật',
                'full_content': 'Bài viết về công nghệ AI và robot thông minh',
                'url': 'http://example.com/hidden-tech'
            }
        ]
        
        positive_keywords = {
            'technology': ['AI', 'robot']
        }
        
        result = categorize_positive(articles, positive_keywords)
        assert len(result['technology']) == 1
    
    def test_categorize_positive_multiple_categories(self):
        """Test article matching multiple categories."""
        articles = [
            {
                'title': 'Công nghệ AI trong kinh tế',
                'summary': 'Robot hỗ trợ đầu tư',
                'full_content': 'AI giúp tăng GDP',
                'url': 'http://example.com/multi'
            }
        ]
        
        positive_keywords = {
            'technology': ['công nghệ', 'AI', 'robot'],
            'economy': ['kinh tế', 'đầu tư', 'GDP']
        }
        
        result = categorize_positive(articles, positive_keywords)
        # Article should appear in both categories
        assert len(result['technology']) == 1
        assert len(result['economy']) == 1


class TestSortAndLimit:
    """Test sorting and limiting functionality."""
    
    def test_sort_and_limit_basic(self):
        """Test basic sorting and limiting."""
        now = datetime.now(timezone(timedelta(hours=7)))
        
        categorized = {
            'technology': [
                {
                    'title': 'Old tech news',
                    'publish_time': now - timedelta(hours=2),
                    'url': 'http://example.com/old-tech'
                },
                {
                    'title': 'New tech news',
                    'publish_time': now,
                    'url': 'http://example.com/new-tech'
                }
            ],
            'economy': [
                {
                    'title': 'Economy news',
                    'publish_time': now - timedelta(hours=1),
                    'url': 'http://example.com/economy'
                }
            ]
        }
        
        result = sort_and_limit(categorized, limit=3)
        
        # Should be sorted by publish_time (newest first)
        assert len(result) == 3
        assert result[0]['title'] == 'New tech news'
        assert result[1]['title'] == 'Economy news'
        assert result[2]['title'] == 'Old tech news'
    
    def test_sort_and_limit_deduplication(self):
        """Test deduplication functionality."""
        now = datetime.now(timezone(timedelta(hours=7)))
        
        categorized = {
            'technology': [
                {
                    'title': 'Duplicate article',
                    'publish_time': now,
                    'url': 'http://example.com/duplicate'
                },
                {
                    'title': 'Unique article',
                    'publish_time': now - timedelta(hours=1),
                    'url': 'http://example.com/unique'
                }
            ],
            'economy': [
                {
                    'title': 'Duplicate article',
                    'publish_time': now,
                    'url': 'http://example.com/duplicate'  # Same URL as above
                }
            ]
        }
        
        result = sort_and_limit(categorized, limit=5)
        
        # Should remove duplicates
        assert len(result) == 2
        urls = [article['url'] for article in result]
        assert len(set(urls)) == 2  # All URLs should be unique
    
    def test_sort_and_limit_round_robin(self):
        """Test round-robin selection across categories."""
        now = datetime.now(timezone(timedelta(hours=7)))
        
        categorized = {
            'technology': [
                {'title': 'Tech 1', 'publish_time': now, 'url': 'http://example.com/tech1'},
                {'title': 'Tech 2', 'publish_time': now, 'url': 'http://example.com/tech2'},
                {'title': 'Tech 3', 'publish_time': now, 'url': 'http://example.com/tech3'}
            ],
            'economy': [
                {'title': 'Econ 1', 'publish_time': now, 'url': 'http://example.com/econ1'},
                {'title': 'Econ 2', 'publish_time': now, 'url': 'http://example.com/econ2'}
            ]
        }
        
        result = sort_and_limit(categorized, limit=4)
        
        # Should get diverse selection (round-robin)
        assert len(result) == 4
        titles = [article['title'] for article in result]
        # Should have articles from both categories
        tech_count = len([t for t in titles if 'Tech' in t])
        econ_count = len([t for t in titles if 'Econ' in t])
        assert tech_count >= 1
        assert econ_count >= 1


class TestCompleteFilteringPipeline:
    """Test the complete filtering pipeline."""
    
    def test_filter_and_select_complete_pipeline(self):
        """Test the complete filtering pipeline."""
        now = datetime.now(timezone(timedelta(hours=7)))
        
        articles = [
            {
                'title': 'Công nghệ AI mới nhất',
                'summary': 'Robot thông minh phát triển',
                'full_content': 'Chi tiết về trí tuệ nhân tạo',
                'publish_time': now,
                'url': 'http://example.com/ai'
            },
            {
                'title': 'Tai nạn giao thông',
                'summary': 'Vụ tai nạn nghiêm trọng',
                'full_content': 'Nhiều người bị thương',
                'publish_time': now - timedelta(hours=1),
                'url': 'http://example.com/accident'
            },
            {
                'title': 'Tăng trưởng GDP',
                'summary': 'Kinh tế phát triển tích cực',
                'full_content': 'Đầu tư tăng mạnh',
                'publish_time': now - timedelta(hours=2),
                'url': 'http://example.com/gdp'
            },
            {
                'title': 'Học sinh bị đánh',
                'summary': 'Bạo lực học đường',
                'full_content': 'Túm tóc và đấm đá',
                'publish_time': now - timedelta(hours=3),
                'url': 'http://example.com/violence'
            }
        ]
        
        positive_keywords = {
            'technology': ['công nghệ', 'AI', 'robot'],
            'economy': ['GDP', 'kinh tế', 'đầu tư']
        }
        
        negative_keywords = ['tai nạn', 'đánh', 'bạo lực', 'túm tóc']
        
        result = filter_and_select(articles, positive_keywords, negative_keywords, limit=3)
        
        # Should filter out negative articles and select positive ones
        assert len(result) == 2  # Only tech and economy articles should remain
        titles = [article['title'] for article in result]
        assert any('AI' in title for title in titles)
        assert any('GDP' in title for title in titles)
        assert not any('tai nạn' in title for title in titles)
        assert not any('đánh' in title for title in titles)
    
    def test_filter_and_select_with_duplicates(self):
        """Test filtering pipeline with duplicate articles."""
        now = datetime.now(timezone(timedelta(hours=7)))
        
        articles = [
            {
                'title': 'Công nghệ mới',
                'summary': 'AI phát triển',
                'publish_time': now,
                'url': 'http://example.com/tech'
            },
            {
                'title': 'Công nghệ mới',  # Same title
                'summary': 'AI phát triển',  # Same summary
                'publish_time': now,
                'url': 'http://example.com/tech'  # Same URL - duplicate
            },
            {
                'title': 'Kinh tế tăng trưởng',
                'summary': 'GDP tăng cao',
                'publish_time': now,
                'url': 'http://example.com/economy'
            }
        ]
        
        positive_keywords = {
            'technology': ['công nghệ', 'AI'],
            'economy': ['kinh tế', 'GDP']
        }
        
        result = filter_and_select(articles, positive_keywords, [], limit=5)
        
        # Should remove duplicates
        assert len(result) == 2
        urls = [article['url'] for article in result]
        assert len(set(urls)) == 2


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_articles_list(self):
        """Test with empty articles list."""
        result = filter_and_select([], {'tech': ['AI']}, ['accident'], limit=5)
        assert result == []
    
    def test_no_matching_articles(self):
        """Test when no articles match positive keywords."""
        articles = [
            {
                'title': 'Tin tức thời tiết',
                'summary': 'Dự báo mưa',
                'url': 'http://example.com/weather'
            }
        ]
        
        positive_keywords = {'technology': ['AI', 'robot']}
        result = filter_and_select(articles, positive_keywords, [], limit=5)
        assert result == []
    
    def test_all_articles_filtered_by_negative_keywords(self):
        """Test when all articles are filtered out by negative keywords."""
        articles = [
            {
                'title': 'Tai nạn nghiêm trọng',
                'summary': 'Nhiều người chết',
                'url': 'http://example.com/accident'
            }
        ]
        
        positive_keywords = {'news': ['tai nạn']}  # Positive keyword matches...
        negative_keywords = ['tai nạn', 'chết']    # But negative keywords filter it out
        
        result = filter_and_select(articles, positive_keywords, negative_keywords, limit=5)
        assert result == []
    
    def test_missing_fields_in_articles(self):
        """Test with articles missing some fields."""
        articles = [
            {
                'title': 'Công nghệ AI',
                # Missing summary, full_content, publish_time
                'url': 'http://example.com/incomplete'
            }
        ]
        
        positive_keywords = {'technology': ['AI']}
        result = filter_and_select(articles, positive_keywords, [], limit=5)
        
        # Should still work with missing fields
        assert len(result) == 1
        assert result[0]['title'] == 'Công nghệ AI'