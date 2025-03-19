import os
import json
from loguru import logger
from menu_scraper import MenuScraper

def configure_lambda_logging():
    """Configure logging for AWS Lambda environment."""
    # Remove default logger to reconfigure for Lambda
    logger.remove()
    # Add Lambda-compatible logger
    logger.add(
        lambda msg: print(msg),  # Lambda logs through stdout
        level=os.getenv('LOG_LEVEL', 'INFO'),
        format="{time} | {level} | {message}"
    )

def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    Args:
        event: The event data passed to the function
        context: Runtime information provided by AWS Lambda
    Returns:
        dict: Response object for AWS Lambda
    """
    try:
        # Configure logging for Lambda environment
        configure_lambda_logging()
        logger.info("Starting menu scraper Lambda function")
        
        # Initialize and run the scraper
        scraper = MenuScraper()
        scraper.run()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Menu scraping completed successfully',
                'timestamp': event.get('time', '')
            })
        }
    except Exception as e:
        logger.error(f"Lambda execution failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Menu scraping failed',
                'error': str(e)
            })
        } 