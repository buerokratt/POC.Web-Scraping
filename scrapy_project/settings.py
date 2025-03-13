"""Scrapy settings file."""

import os
from config.app_config import Config
from models.database import get_db_session

BOT_NAME = Config.SCRAPY_PROJECT_NAME

SPIDER_MODULES = ['scrapy_project.spiders']
NEWSPIDER_MODULE = 'scrapy_project.spiders'

USER_AGENT = Config.USER_AGENT
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': USER_AGENT
}

#Should we be nice and obey it?
ROBOTSTXT_OBEY = True

FEEDS = {
    'output.json': {  # This is the output file
        'format': 'json',  # The format for the data (you can change this to csv, xml, etc.)
        'encoding': 'utf8',  # Encoding for the output file
        'store_empty': False,  # Skip empty items
        'indent': 4,  # Pretty-print the output file with indentation
    },
}

# Use Playwright with Chromium (you can also use 'firefox' or 'webkit')
PLAYWRIGHT_BROWSER_TYPE = 'chromium'
PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": True}

# Set concurrency limits from environment variables or use defaults
CONCURRENT_REQUESTS = int(os.getenv("CONCURRENT_REQUESTS", 48))
CONCURRENT_REQUESTS_PER_DOMAIN = int(os.getenv("CONCURRENT_REQUESTS_PER_DOMAIN", 24))
CONCURRENT_REQUESTS_PER_IP = int(os.getenv("CONCURRENT_REQUESTS_PER_IP", 24))
REACTOR_THREADPOOL_MAXSIZE = int(os.getenv("REACTOR_THREADPOOL_MAXSIZE", 30))

LOG_ENABLED = True  # Ensure logging is enabled
LOG_LEVEL = 'INFO'  # Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_STDOUT = True  # Redirect Scrapy's logs to the terminal (STDOUT)

DB_SESSION_FACTORY = get_db_session
