"""
Unit tests for email sending functionality.
"""

import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_send_email_success():
    """Test successful email sending."""
    from email_sender import send_email
    
    smtp_config = {
        'host': 'smtp.gmail.com',
        'port': 587,
        'username': 'test@example.com',
        'password': 'password'
    }
    
    recipients = ['recipient1@example.com', 'recipient2@example.com']
    subject = 'Test Subject'
    html_body = '<html><body>Test Body</body></html>'
    
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        result = send_email(html_body, subject, recipients, smtp_config)
        
        # Verify SMTP calls
        mock_smtp.assert_called_once_with(smtp_config['host'], smtp_config['port'])
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(smtp_config['username'], smtp_config['password'])
        mock_server.quit.assert_called_once()
        
        # Should return True for success
        assert result == True


def test_send_email_smtp_error():
    """Test email sending with SMTP error."""
    from email_sender import send_email
    import smtplib
    
    smtp_config = {
        'host': 'smtp.gmail.com',
        'port': 587,
        'username': 'test@example.com',
        'password': 'password'
    }
    
    recipients = ['recipient@example.com']
    subject = 'Test Subject'
    html_body = '<html><body>Test Body</body></html>'
    
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, 'Authentication failed')
        
        result = send_email(html_body, subject, recipients, smtp_config)
        
        # Should return False for failure
        assert result == False


def test_send_email_with_retries():
    """Test email sending with retry mechanism."""
    from email_sender import send_email_with_retries
    import smtplib
    
    smtp_config = {
        'host': 'smtp.gmail.com',
        'port': 587,
        'username': 'test@example.com',
        'password': 'password'
    }
    
    recipients = ['recipient@example.com']
    subject = 'Test Subject'
    html_body = '<html><body>Test Body</body></html>'
    
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Fail first 2 attempts, succeed on 3rd
        mock_server.login.side_effect = [
            smtplib.SMTPException('Connection failed'),
            smtplib.SMTPException('Connection failed'),
            None  # Success
        ]
        
        result = send_email_with_retries(html_body, subject, recipients, smtp_config, max_retries=3)
        
        # Should succeed after retries
        assert result == True
        assert mock_smtp.call_count == 3


def test_send_email_max_retries_exceeded():
    """Test email sending when max retries exceeded."""
    from email_sender import send_email_with_retries
    import smtplib
    
    smtp_config = {
        'host': 'smtp.gmail.com',
        'port': 587,
        'username': 'test@example.com',
        'password': 'password'
    }
    
    recipients = ['recipient@example.com']
    subject = 'Test Subject'
    html_body = '<html><body>Test Body</body></html>'
    
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        mock_server.login.side_effect = smtplib.SMTPException('Persistent error')
        
        result = send_email_with_retries(html_body, subject, recipients, smtp_config, max_retries=3)
        
        # Should fail after max retries
        assert result == False
        assert mock_smtp.call_count == 3


def test_create_email_message():
    """Test email message creation with proper headers."""
    from email_sender import create_email_message
    
    subject = 'Test Subject'
    html_body = '<html><body>Test Body</body></html>'
    sender = 'sender@example.com'
    recipients = ['recipient1@example.com', 'recipient2@example.com']
    
    message = create_email_message(subject, html_body, sender, recipients)
    
    # Check headers
    assert message['Subject'] == subject
    assert message['From'] == sender
    assert message['To'] == ', '.join(recipients)
    
    # Check content type (multipart message containing HTML)
    assert message.get_content_type() == 'multipart/alternative'
    
    # Check that HTML part exists
    parts = message.get_payload()
    assert len(parts) == 1
    assert parts[0].get_content_type() == 'text/html'
    
    # Check encoding
    assert 'utf-8' in str(message)


def test_validate_email_config():
    """Test email configuration validation."""
    from email_sender import validate_email_config
    
    # Valid config
    valid_config = {
        'host': 'smtp.gmail.com',
        'port': 587,
        'username': 'test@example.com',
        'password': 'password'
    }
    
    assert validate_email_config(valid_config) == True
    
    # Invalid config - missing fields
    invalid_config = {
        'host': 'smtp.gmail.com',
        'port': 587
        # Missing username and password
    }
    
    assert validate_email_config(invalid_config) == False
    
    # Invalid config - wrong port type
    invalid_config2 = {
        'host': 'smtp.gmail.com',
        'port': 'not_a_number',
        'username': 'test@example.com',
        'password': 'password'
    }
    
    assert validate_email_config(invalid_config2) == False