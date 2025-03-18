import os
from dotenv import load_dotenv
from loguru import logger
from menu_scraper import MenuScraper

def main():
    """Main function to run the menu scraper once."""
    load_dotenv()
    
    # Configure logging
    logger.add(
        "logs/scheduler.log",
        rotation="1 day",
        retention="7 days",
        level=os.getenv('LOG_LEVEL', 'INFO')
    )
    
    try:
        scraper = MenuScraper()
        scraper.run()
    except Exception as e:
        logger.error(f"Failed to run menu scraper: {str(e)}")

if __name__ == "__main__":
    main() 