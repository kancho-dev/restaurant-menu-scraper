import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from loguru import logger
from playwright.sync_api import sync_playwright, Page, Browser
import requests
from PIL import Image

class MenuScraper:
    """A class to scrape daily lunch menu images from Facebook and share them on Google Chat."""
    
    def __init__(self):
        """Initialize the MenuScraper with configuration from environment variables."""
        load_dotenv()
        
        # Load configuration
        self.fb_page_url = os.getenv('FACEBOOK_PAGE_URL')
        self.webhook_url = os.getenv('GOOGLE_CHAT_WEBHOOK_URL')
        
        # Screenshot directory is optional
        screenshot_dir = os.getenv('SCREENSHOT_DIR')
        self.screenshot_dir = Path(screenshot_dir) if screenshot_dir else None
        
        # Create screenshots directory if specified and doesn't exist
        if self.screenshot_dir:
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Screenshot directory set to: {self.screenshot_dir}")
        else:
            logger.info("Screenshot saving is disabled")
    
    def find_todays_menu_post(self, page: Page) -> Optional[str]:
        """Find today's menu post and return the image URL if found."""
        logger.info("Searching for today's menu post...")
        
        try:
            # Use a reasonable timeout
            page.set_default_timeout(30000)  # 30 seconds is plenty
            
            logger.info(f"Navigating to {self.fb_page_url}")
            response = page.goto(self.fb_page_url, wait_until='networkidle')
            
            # Take a screenshot right after page load for debugging (only if screenshot_dir is set)
            if self.screenshot_dir:
                debug_path = self.screenshot_dir / "initial_load.png"
                page.screenshot(path=str(debug_path))
                logger.info(f"Saved initial page screenshot to {debug_path}")
            
            # Log the page title to verify we're on the right page
            logger.info(f"Page title: {page.title()}")
            
            # Try different selectors for posts
            selectors = [
                'div[role="article"]',  # Original selector
                'div[data-pagelet="FeedUnit"]',  # Alternative FB feed selector
                'div.x1yztbdb',  # FB post class
                'div.x1lliihq'   # FB content class
            ]
            
            posts = []
            for selector in selectors:
                posts = page.query_selector_all(selector)
                if len(posts) > 0:
                    logger.info(f"Found {len(posts)} posts using selector: {selector}")
                    break
            
            if len(posts) == 0:
                logger.warning("No posts found with any selector")
                # Save page content for debugging if screenshot directory is set
                if self.screenshot_dir:
                    content = page.content()
                    debug_html = self.screenshot_dir / "page_content.html"
                    with open(debug_html, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"Saved page HTML to {debug_html}")
                return None
            
            # Look for posts from today
            today = datetime.now().strftime("%B %d")
            logger.info(f"Looking for posts from: {today}")
            
            for idx, post in enumerate(posts):
                try:
                    # Log the post text content for debugging
                    post_text = post.text_content()
                    logger.info(f"Post {idx} content preview: {post_text[:100]}...")
                    
                    # Check for images first
                    images = post.query_selector_all('img[src*="https"]')
                    if images:
                        logger.info(f"Found {len(images)} images in post {idx}")
                        
                        for image in images:
                            image_url = image.get_attribute('src')
                            if image_url:
                                logger.info(f"Found image URL: {image_url[:100]}...")
                                return image_url
                    
                except Exception as e:
                    logger.error(f"Error processing post {idx}: {str(e)}")
                    continue
            
            logger.warning(f"No suitable images found in any posts")
            return None
            
        except Exception as e:
            logger.error(f"Error finding menu post: {str(e)}")
            raise
    
    def send_to_google_chat(self, image_url: str) -> None:
        """Send the menu image to Google Chat using webhook."""
        logger.info("Sending menu to Google Chat...")
        
        try:
            # Prepare the message with card format including the image
            message = {
                "cards": [{
                    "header": {
                        "title": f"🍽️ Обедното меню за днес ({datetime.now().strftime('%d-%m-%Y')})"
                    },
                    "sections": [{
                        "widgets": [{
                            "image": {
                                "imageUrl": image_url,
                                "onClick": {
                                    "openLink": {
                                        "url": image_url
                                    }
                                }
                            }
                        }]
                    }]
                }]
            }
            
            # Send to webhook
            response = requests.post(
                self.webhook_url,
                headers={"Content-Type": "application/json"},
                json=message
            )
            response.raise_for_status()
            
            logger.info("Successfully sent menu to Google Chat")
            
        except Exception as e:
            logger.error(f"Failed to send menu to Google Chat: {str(e)}")
            raise
    
    def clean_old_images(self) -> None:
        """Remove menu images older than 2 days from the screenshots directory."""
        if not self.screenshot_dir:
            return
            
        logger.info("Cleaning old menu images...")
        try:
            today = datetime.now()
            # Get all menu_*.png files
            for image_file in self.screenshot_dir.glob("menu_*.png"):
                try:
                    # Extract date from filename (format: menu_YYYYMMDD.png)
                    date_str = image_file.stem.split('_')[1]
                    file_date = datetime.strptime(date_str, '%Y%m%d')
                    
                    # If image is older than 2 days, delete it
                    if (today - file_date).days > 2:
                        logger.info(f"Removing old menu image: {image_file.name}")
                        image_file.unlink()
                except (ValueError, IndexError) as e:
                    logger.warning(f"Could not parse date from filename {image_file.name}: {str(e)}")
                    continue
                
        except Exception as e:
            logger.error(f"Error cleaning old images: {str(e)}")
            # Don't raise the exception - we don't want to break the main flow if cleanup fails
    
    def run(self) -> None:
        """Main execution method to scrape and share the menu."""
        logger.info("Starting menu scraping process...")
        
        try:
            with sync_playwright() as p:
                # Launch browser with desktop viewport and common browser flags
                browser: Browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--disable-gpu'
                    ]
                )
                
                context = browser.new_context(
                    viewport={'width': 1280, 'height': 800},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                    locale='en-US',
                )
                
                # Add common browser properties to appear more like a real browser
                page = context.new_page()
                page.evaluate("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                """)
                
                # Find menu image URL
                image_url = self.find_todays_menu_post(page)
                if image_url:
                    # Save image locally only if screenshot directory is configured
                    if self.screenshot_dir:
                        image_path = self.screenshot_dir / f"menu_{datetime.now().strftime('%Y%m%d')}.png"
                        page.goto(image_url)
                        page.screenshot(path=str(image_path))
                        
                        # Clean old images after successfully saving new one
                        self.clean_old_images()
                        
                        # Validate saved image
                        try:
                            with Image.open(image_path) as img:
                                width, height = img.size
                                logger.info(f"Successfully saved image: {image_path}")
                                logger.info(f"Image size: {width}x{height} pixels")
                                logger.info(f"Image format: {img.format}")
                                
                                # Basic validation
                                if width < 100 or height < 100:
                                    logger.warning("Image seems too small, might not be a valid menu")
                                
                                if os.path.getsize(image_path) < 1024:  # Less than 1KB
                                    logger.warning("Image file is suspiciously small")
                        except Exception as e:
                            logger.error(f"Failed to validate saved image: {str(e)}")
                            # Don't raise here, we can still try to send to Google Chat
                    
                    # Send to Google Chat using the original Facebook image URL
                    self.send_to_google_chat(image_url)
                else:
                    logger.warning("No menu found for today")
                
                browser.close()
                
        except Exception as e:
            logger.error(f"Error in menu scraping process: {str(e)}")
            raise 