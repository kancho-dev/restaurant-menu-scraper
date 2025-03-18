# Restaurant Menu Scraper

Automatically scrape daily lunch menu images from a Facebook page and share them with your colleagues via Google Chat.

## Features

- 🤖 Automated Facebook page scraping
- 📸 Menu image extraction
- 💬 Google Chat integration
- ⏰ Scheduled daily runs
- 📝 Detailed logging

## Prerequisites

- Python 3.8+
- Facebook account with access to the target page
- Google Chat webhook URL

## Installation

1. Clone this repository:
```bash
git clone https://github.com/kancho-dev/restaurant-menu-scraper.git
cd restaurant-menu-scraper
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install chromium
```

5. Configure the environment:
```bash
cp config/.env.example .env
```

Edit the `.env` file with your:
- Facebook credentials
- Target Facebook page URL
- Google Chat webhook URL
- Desired schedule time

## Usage

Run the scraper scheduler:
```bash
python src/main.py
```

The script will:
1. Run at the configured time daily (default: 11:00)
2. Log into Facebook
3. Find today's menu post
4. Extract and save the menu image
5. Share it in your Google Chat

## Logging

Logs are stored in the `logs` directory:
- `menu_scraper.log`: Scraping process logs
- `scheduler.log`: Scheduler process logs

## Security Notes

- Store your Facebook credentials securely
- Never commit the `.env` file
- Use a dedicated Facebook account for scraping if possible

## Troubleshooting

1. **No menu found**: Check if:
   - The Facebook page is accessible
   - The menu was posted today
   - The post contains an image

2. **Login failed**: Verify:
   - Facebook credentials in `.env`
   - Account 2FA is disabled
   - Account has no pending security checks

3. **Google Chat errors**: Confirm:
   - Webhook URL is correct
   - Webhook has proper permissions
   - Image is accessible to Google Chat