"""
Email sending module for news filtering system.
Handles SMTP email delivery with retry mechanism and error handling.
"""

import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
import logging


def validate_email_config(smtp_config: Dict[str, Any]) -> bool:
    """
    Validate SMTP configuration.
    
    Args:
        smtp_config: SMTP configuration dictionary
        
    Returns:
        True if configuration is valid, False otherwise
    """
    required_fields = ['host', 'port', 'username', 'password']
    
    for field in required_fields:
        if field not in smtp_config or not smtp_config[field]:
            logging.error(f"Missing or empty required field: {field}")
            return False
    
    # Validate port is integer
    try:
        int(smtp_config['port'])
    except (ValueError, TypeError):
        logging.error(f"Invalid port number: {smtp_config['port']}")
        return False
    
    return True


def create_email_message(subject: str, html_body: str, sender: str, recipients: List[str]) -> MIMEMultipart:
    """
    Create email message with proper headers and content.
    
    Args:
        subject: Email subject
        html_body: HTML email body
        sender: Sender email address
        recipients: List of recipient email addresses
        
    Returns:
        MIMEMultipart email message object
    """
    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = ', '.join(recipients)
    
    # Add HTML content
    html_part = MIMEText(html_body, 'html', 'utf-8')
    message.attach(html_part)
    
    return message


def send_email(html_body: str, subject: str, recipients: List[str], smtp_config: Dict[str, Any]) -> bool:
    """
    Send email via SMTP.
    
    Args:
        html_body: HTML email body
        subject: Email subject
        recipients: List of recipient email addresses
        smtp_config: SMTP configuration dictionary
        
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Validate configuration
        if not validate_email_config(smtp_config):
            return False
        
        if not recipients:
            logging.error("No recipients specified")
            return False
        
        # Create email message
        sender = smtp_config['username']
        message = create_email_message(subject, html_body, sender, recipients)
        
        # Connect to SMTP server
        server = smtplib.SMTP(smtp_config['host'], smtp_config['port'])
        
        # Enable TLS encryption
        server.starttls()
        
        # Login to server
        server.login(smtp_config['username'], smtp_config['password'])
        
        # Send email
        server.sendmail(sender, recipients, message.as_string())
        
        # Close connection
        server.quit()
        
        logging.info(f"Email sent successfully to {len(recipients)} recipients")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"SMTP Authentication failed: {e}")
        return False
        
    except smtplib.SMTPRecipientsRefused as e:
        logging.error(f"Recipients refused: {e}")
        return False
        
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error: {e}")
        return False
        
    except Exception as e:
        logging.error(f"Unexpected error sending email: {e}")
        return False


def send_email_with_retries(html_body: str, subject: str, recipients: List[str], smtp_config: Dict[str, Any], max_retries: int = 3) -> bool:
    """
    Send email with retry mechanism.
    
    Args:
        html_body: HTML email body
        subject: Email subject
        recipients: List of recipient email addresses
        smtp_config: SMTP configuration dictionary
        max_retries: Maximum number of retry attempts
        
    Returns:
        True if email sent successfully, False otherwise
    """
    for attempt in range(max_retries):
        logging.info(f"Email sending attempt {attempt + 1}/{max_retries}")
        
        success = send_email(html_body, subject, recipients, smtp_config)
        
        if success:
            return True
        
        if attempt < max_retries - 1:  # Don't sleep after last attempt
            wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
            logging.info(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    
    logging.error(f"Failed to send email after {max_retries} attempts")
    return False


def send_notification_email(articles: List[Dict[str, Any]], config: 'Config') -> bool:
    """
    Send notification email using configuration.
    
    Args:
        articles: List of articles for email content
        config: Configuration object with email settings
        
    Returns:
        True if email sent successfully, False otherwise
    """
    from datetime import datetime, timezone, timedelta
    from email_generator import generate_email_body
    
    try:
        # Generate email content
        current_date = datetime.now(timezone(timedelta(hours=7)))
        subject, html_body = generate_email_body(articles, current_date)
        
        # Get recipients and SMTP config
        recipients = config.email_recipients
        smtp_config = config.smtp_config
        
        if not recipients:
            logging.warning("No email recipients configured")
            return False
        
        # Send email with retries
        return send_email_with_retries(html_body, subject, recipients, smtp_config)
        
    except Exception as e:
        logging.error(f"Error in send_notification_email: {e}")
        return False