import os
import time
from datetime import datetime
import schedule
from dotenv import load_dotenv
from loguru import logger

from menu_scraper import MenuScraper

def run_scraper():
    """Execute the menu scraping process."""
    try:
        scraper = MenuScraper()
        scraper.run()
    except Exception as e:
        logger.error(f"Failed to run menu scraper: {str(e)}")

def main():
    """Main function to schedule and run the menu scraper."""
    load_dotenv()
    
    # Configure logging
    logger.add(
        "logs/scheduler.log",
        rotation="1 day",
        retention="7 days",
        level=os.getenv('LOG_LEVEL', 'INFO')
    )
    
    # Get schedule time from environment (default to 11:00)
    schedule_time = os.getenv('SCHEDULE_TIME', '11:00')
    
    logger.info(f"Starting scheduler, will run daily at {schedule_time}")
    
    # Schedule the job
    schedule.every().day.at(schedule_time).do(run_scraper)
    
    # Run immediately if started after schedule time
    current_time = datetime.now().strftime("%H:%M")
    if current_time > schedule_time:
        logger.info("Running initial scrape as we're past schedule time")
        run_scraper()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 