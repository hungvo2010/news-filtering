"""
Unit tests for scheduler functionality.
"""

import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
import pytest

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_setup_scheduler():
    """Test scheduler setup with correct timing."""
    from scheduler import setup_scheduler
    
    with patch('scheduler.BlockingScheduler') as mock_scheduler_class:
        mock_scheduler = MagicMock()
        mock_scheduler_class.return_value = mock_scheduler
        
        # Mock pipeline function
        mock_pipeline = Mock()
        
        scheduler = setup_scheduler(mock_pipeline)
        
        # Verify scheduler was created
        mock_scheduler_class.assert_called_once()
        
        # Verify job was scheduled (daily at 07:00 +07)
        mock_scheduler.add_job.assert_called_once()
        call_args = mock_scheduler.add_job.call_args
        
        # Check that the job function is correct
        assert call_args[0][0] == mock_pipeline  # First argument is the function
        
        # Check scheduling parameters
        kwargs = call_args[1]
        assert kwargs['trigger'] == 'cron'
        assert kwargs['hour'] == 7
        assert kwargs['minute'] == 0
        assert kwargs['timezone'] == 'Asia/Ho_Chi_Minh'


def test_create_pipeline_function():
    """Test pipeline function creation and execution."""
    from scheduler import create_pipeline_function
    
    # Mock configuration
    mock_config = Mock()
    mock_config.rss_sources = ['http://example.com/rss']
    mock_config.scraping_sources = {'test': {'url': 'http://test.com'}}
    mock_config.positive_keywords = {'tech': ['AI', 'robot']}
    mock_config.negative_keywords = ['negative']
    mock_config.email_recipients = ['test@example.com']
    mock_config.smtp_config = {'host': 'smtp.test.com', 'port': 587, 'username': 'test', 'password': 'pass'}
    
    # Create pipeline function
    pipeline_func = create_pipeline_function(mock_config)
    
    with patch('scheduler.fetch_articles') as mock_fetch, \
         patch('scheduler.filter_and_select') as mock_filter, \
         patch('scheduler.send_notification_email') as mock_send:
        
        mock_fetch.return_value = [
            {'title': 'Test Article', 'summary': 'Test', 'url': 'http://test.com', 'source': 'test'}
        ]
        mock_filter.return_value = [
            {'title': 'Filtered Article', 'summary': 'Filtered', 'url': 'http://test.com', 'source': 'test'}
        ]
        mock_send.return_value = True
        
        # Execute pipeline
        pipeline_func()
        
        # Verify all steps were called
        mock_fetch.assert_called_once()
        mock_filter.assert_called_once()
        mock_send.assert_called_once()


def test_pipeline_with_no_articles():
    """Test pipeline behavior when no articles are found."""
    from scheduler import create_pipeline_function
    
    mock_config = Mock()
    mock_config.rss_sources = []
    mock_config.scraping_sources = {}
    mock_config.positive_keywords = {}
    mock_config.negative_keywords = []
    mock_config.email_recipients = ['test@example.com']
    mock_config.smtp_config = {'host': 'smtp.test.com', 'port': 587, 'username': 'test', 'password': 'pass'}
    
    pipeline_func = create_pipeline_function(mock_config)
    
    with patch('scheduler.fetch_articles') as mock_fetch, \
         patch('scheduler.filter_and_select') as mock_filter, \
         patch('scheduler.send_notification_email') as mock_send:
        
        mock_fetch.return_value = []
        mock_filter.return_value = []
        mock_send.return_value = True
        
        # Execute pipeline
        pipeline_func()
        
        # Verify email is still sent (with fallback content)
        mock_send.assert_called_once_with([], mock_config)


def test_pipeline_error_handling():
    """Test pipeline error handling."""
    from scheduler import create_pipeline_function
    
    mock_config = Mock()
    mock_config.rss_sources = ['http://example.com/rss']
    mock_config.scraping_sources = {}
    mock_config.positive_keywords = {'tech': ['AI']}
    mock_config.negative_keywords = []
    mock_config.email_recipients = ['test@example.com']
    mock_config.smtp_config = {'host': 'smtp.test.com', 'port': 587, 'username': 'test', 'password': 'pass'}
    
    pipeline_func = create_pipeline_function(mock_config)
    
    with patch('scheduler.fetch_articles') as mock_fetch, \
         patch('scheduler.filter_and_select') as mock_filter, \
         patch('scheduler.send_notification_email') as mock_send, \
         patch('scheduler.logging') as mock_logging:
        
        # Simulate fetch error
        mock_fetch.side_effect = Exception("Fetch failed")
        
        # Pipeline should handle error gracefully
        pipeline_func()
        
        # Verify error was logged
        mock_logging.error.assert_called()


def test_run_scheduler():
    """Test scheduler execution."""
    from scheduler import run_scheduler
    
    with patch('scheduler.setup_scheduler') as mock_setup, \
         patch('scheduler.create_pipeline_function') as mock_create_pipeline:
        
        mock_scheduler = MagicMock()
        mock_setup.return_value = mock_scheduler
        
        mock_pipeline = Mock()
        mock_create_pipeline.return_value = mock_pipeline
        
        mock_config = Mock()
        
        run_scheduler(mock_config)
        
        # Verify pipeline was created and scheduler was set up
        mock_create_pipeline.assert_called_once_with(mock_config)
        mock_setup.assert_called_once_with(mock_pipeline)
        mock_scheduler.start.assert_called_once()


def test_scheduler_timezone():
    """Test that scheduler uses correct timezone."""
    from scheduler import get_vietnam_timezone
    
    tz = get_vietnam_timezone()
    
    # Should be UTC+7
    utc_offset = tz.utcoffset(datetime.now())
    assert utc_offset == timedelta(hours=7)


def test_scheduler_job_id():
    """Test that scheduled job has proper ID for management."""
    from scheduler import setup_scheduler
    
    with patch('scheduler.BlockingScheduler') as mock_scheduler_class:
        mock_scheduler = MagicMock()
        mock_scheduler_class.return_value = mock_scheduler
        
        mock_pipeline = Mock()
        
        setup_scheduler(mock_pipeline)
        
        # Verify job was added with ID
        call_kwargs = mock_scheduler.add_job.call_args[1]
        assert 'id' in call_kwargs
        assert call_kwargs['id'] == 'daily_news_job'