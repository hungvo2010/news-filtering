"""
Main entry point for News Filter application.
Provides options to run scheduler or execute pipeline once.
"""

import sys
import os
import logging
import argparse
from datetime import datetime, timezone, timedelta

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import config
from scraper import fetch_articles
from filter import filter_and_select
from email_sender import send_notification_email

# Import scheduler functions conditionally
try:
    from scheduler import run_scheduler, run_once
    SCHEDULER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Scheduler not available: {e}")
    SCHEDULER_AVAILABLE = False


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('news_filter.log'),
            logging.StreamHandler()
        ]
    )


def test_configuration():
    """Test and display configuration settings."""
    print("News Filter Application - Configuration Test")
    print("=" * 60)
    
    print(f"SMTP Host: {config.smtp_config['host']}")
    print(f"Email Recipients: {len(config.email_recipients)} recipients")
    print(f"Positive Keywords: {list(config.positive_keywords.keys())}")
    print(f"Negative Keywords Count: {len(config.negative_keywords)}")
    print(f"RSS Sources: {len(config.rss_sources)}")
    print(f"Scraping Sources: {len(config.scraping_sources)}")
    print(f"Timezone: {config.timezone}")
    print()


def test_pipeline():
    """Test the complete pipeline once."""
    print("News Filter Application - Pipeline Test")
    print("=" * 60)
    
    # Get current date
    current_date = datetime.now(timezone(timedelta(hours=7)))
    print(f"Current date: {current_date.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Step 1: Fetch articles
    print("\n1. Fetching articles...")
    sources = {
        'rss': config.rss_sources,
        'scraping': config.scraping_sources
    }
    
    articles = fetch_articles(sources, current_date)
    print(f"   Fetched {len(articles)} articles total")
    
    # Display first few raw articles
    for i, article in enumerate(articles[:3]):
        print(f"   Raw Article {i+1}: {article['title'][:60]}... ({article['source']})")
    
    # Step 2: Filter and select
    print("\n2. Filtering and selecting articles...")
    filtered_articles = filter_and_select(
        articles, 
        config.positive_keywords, 
        config.negative_keywords,
        limit=5
    )
    print(f"   Selected {len(filtered_articles)} articles after filtering")
    
    # Display filtered articles
    for i, article in enumerate(filtered_articles):
        print(f"   Selected Article {i+1}: {article['title'][:60]}... ({article['source']})")
    
    # Step 3: Generate and optionally send email
    print("\n3. Email generation test...")
    from email_generator import generate_email_body
    subject, html_body = generate_email_body(filtered_articles, current_date)
    
    print(f"   Email Subject: {subject}")
    print(f"   Email Body Length: {len(html_body)} characters")
    print(f"   Recipients: {len(config.email_recipients)} configured")
    
    return filtered_articles


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(description='News Filter Application')
    parser.add_argument('--mode', choices=['test', 'run-once', 'schedule'], 
                       default='test',
                       help='Operation mode (default: test)')
    parser.add_argument('--config-only', action='store_true',
                       help='Only test configuration')
    parser.add_argument('--send-email', action='store_true',
                       help='Actually send email in test mode')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        if args.config_only:
            test_configuration()
            
        elif args.mode == 'test':
            test_configuration()
            articles = test_pipeline()
            
            if args.send_email and articles:
                print("\n4. Sending test email...")
                success = send_notification_email(articles, config)
                if success:
                    print("   ✓ Email sent successfully!")
                else:
                    print("   ✗ Email sending failed")
            
        elif args.mode == 'run-once':
            if not SCHEDULER_AVAILABLE:
                print("Error: Scheduler not available. Running pipeline manually...")
                # Manual pipeline execution
                current_date = datetime.now(timezone(timedelta(hours=7)))
                sources = {'rss': config.rss_sources, 'scraping': config.scraping_sources}
                articles = fetch_articles(sources, current_date)
                filtered = filter_and_select(articles, config.positive_keywords, config.negative_keywords)
                success = send_notification_email(filtered, config)
                print(f"Pipeline completed. Email {'sent' if success else 'failed'}.")
            else:
                logger.info("Running pipeline once...")
                run_once(config)
                print("Pipeline execution completed. Check logs for details.")
            
        elif args.mode == 'schedule':
            if not SCHEDULER_AVAILABLE:
                print("Error: Scheduler not available. Cannot run in schedule mode.")
                print("Install missing dependencies or run with --mode=run-once")
                return
            logger.info("Starting scheduled mode...")
            print("Starting scheduler... Press Ctrl+C to stop.")
            print("Scheduled to run daily at 07:00 Vietnam time (+07)")
            run_scheduler(config)
            
    except KeyboardInterrupt:
        print("\nStopped by user")
        logger.info("Application stopped by user")
        
    except Exception as e:
        print(f"Error: {e}")
        logger.error(f"Application error: {e}", exc_info=True)


if __name__ == "__main__":
    main()