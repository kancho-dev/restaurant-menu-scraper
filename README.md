# Restaurant Menu Scraper

Automatically scrape daily lunch menu images from a Facebook page and share them with your colleagues via Google Chat.

## Features

- 🤖 Automated Facebook page scraping
- 📸 Menu image extraction and full-size viewing
- 💬 Google Chat integration with preview cards
- ⏰ System-level scheduling (cron)
- 📝 Detailed logging

## Prerequisites

- Python 3.8+
- Facebook account with access to the target page
- Google Chat webhook URL
- Linux/Mac with cron (or Windows with Task Scheduler)

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

## Setting Up Scheduled Runs

### Linux/Mac (Using Cron)

1. Find the absolute paths for your project and Python virtual environment:
```bash
# Get project path
echo $PWD

# Get virtual environment Python path
echo $PWD/venv/bin/python3
```

2. Open your crontab for editing:
```bash
crontab -e
```

3. Add this line to run the scraper daily at 11:00 AM (adjust the paths and time as needed):
```bash
0 11 * * * cd /absolute/path/to/project && /absolute/path/to/venv/bin/python3 src/main.py
```

To use a different time, modify the cron schedule (in this example, `0 11 * * *`):
- First number (0): Minutes (0-59)
- Second number (11): Hours (0-23)
- Remaining asterisks: Day of month, Month, Day of week

### Windows (Using Task Scheduler)

1. Create a batch script `run_scraper.bat` in your project directory:
```batch
@echo off
cd /d "C:\path\to\your\project"
call venv\Scripts\activate
python src\main.py
```

2. Open Task Scheduler:
   - Create a new Basic Task
   - Set trigger to Daily at 11:00 AM
   - Action: Start a program
   - Program/script: Path to your `run_scraper.bat`

## Manual Usage

You can also run the scraper manually at any time:

```bash
python3 src/main.py
```

The script will:
1. Log into Facebook
2. Find today's menu post
3. Extract and save the menu image
4. Share it in your Google Chat with both preview and full-size viewing options

## Logging

Logs are stored in the `logs` directory:
- `scheduler.log`: Execution logs

## Security Notes

- Store your Facebook credentials securely
- Never commit the `.env` file
- Use a dedicated Facebook account for scraping if possible
- Ensure proper file permissions for cron jobs

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

4. **Cron job not running**: Check:
   - Correct paths in crontab
   - Cron service is running (`systemctl status cron`)
   - Log files for errors
   - File permissions