"""
Scheduler module for automated news filtering and email sending.
Handles daily scheduling at 07:00 Vietnam time (+07).
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timezone, timedelta
import logging
from typing import Callable, Any

# Import other modules
from scraper import fetch_articles
from filter import filter_and_select
from email_sender import send_notification_email


def get_vietnam_timezone():
    """Get Vietnam timezone (+07)."""
    return timezone(timedelta(hours=7))


def create_pipeline_function(config: 'Config') -> Callable[[], None]:
    """
    Create the main pipeline function that fetches, filters and sends emails.
    
    Args:
        config: Configuration object
        
    Returns:
        Pipeline function
    """
    def pipeline():
        """Main pipeline function for daily news processing."""
        try:
            logging.info("Starting daily news pipeline")
            
            # Get current date in Vietnam timezone
            current_date = datetime.now(get_vietnam_timezone())
            logging.info(f"Processing news for date: {current_date.strftime('%Y-%m-%d')}")
            
            # Step 1: Fetch articles from all sources
            sources = {
                'rss': config.rss_sources,
                'scraping': config.scraping_sources
            }
            
            logging.info("Fetching articles from sources...")
            articles = fetch_articles(sources, current_date)
            logging.info(f"Fetched {len(articles)} articles total")
            
            # Step 2: Filter and select articles
            logging.info("Filtering and selecting articles...")
            filtered_articles = filter_and_select(
                articles, 
                config.positive_keywords, 
                config.negative_keywords,
                limit=5
            )
            logging.info(f"Selected {len(filtered_articles)} articles after filtering")
            
            # Step 3: Send email notification
            logging.info("Sending email notification...")
            success = send_notification_email(filtered_articles, config)
            
            if success:
                logging.info("Daily pipeline completed successfully")
            else:
                logging.error("Failed to send email notification")
                
        except Exception as e:
            logging.error(f"Error in daily pipeline: {e}", exc_info=True)
    
    return pipeline


def setup_scheduler(pipeline_func: Callable[[], None]) -> BlockingScheduler:
    """
    Set up the scheduler for daily execution at 07:00 Vietnam time.
    
    Args:
        pipeline_func: Function to execute daily
        
    Returns:
        Configured scheduler
    """
    scheduler = BlockingScheduler()
    
    # Schedule daily at 07:00 Vietnam time
    scheduler.add_job(
        pipeline_func,
        trigger='cron',
        hour=7,
        minute=0,
        timezone='Asia/Ho_Chi_Minh',
        id='daily_news_job',
        name='Daily News Processing',
        max_instances=1  # Prevent overlapping executions
    )
    
    logging.info("Scheduler configured for daily execution at 07:00 Vietnam time")
    return scheduler


def run_scheduler(config: 'Config') -> None:
    """
    Run the scheduler with the given configuration.
    
    Args:
        config: Configuration object
    """
    # Create pipeline function
    pipeline_func = create_pipeline_function(config)
    
    # Set up scheduler
    scheduler = setup_scheduler(pipeline_func)
    
    try:
        logging.info("Starting scheduler...")
        scheduler.start()
    except KeyboardInterrupt:
        logging.info("Scheduler stopped by user")
        scheduler.shutdown()
    except Exception as e:
        logging.error(f"Scheduler error: {e}")
        scheduler.shutdown()


def setup_scheduler_with_config(config: 'Config') -> BlockingScheduler:
    """
    Convenience function to set up scheduler with configuration.
    
    Args:
        config: Configuration object
        
    Returns:
        Configured scheduler ready to start
    """
    pipeline_func = create_pipeline_function(config)
    return setup_scheduler(pipeline_func)


def run_once(config: 'Config') -> None:
    """
    Run the pipeline once immediately (for testing/manual execution).
    
    Args:
        config: Configuration object
    """
    logging.info("Running pipeline once...")
    pipeline_func = create_pipeline_function(config)
    pipeline_func()
    logging.info("One-time execution completed")