"""Main."""


from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from sqlalchemy import and_, func
from datetime import datetime
from urllib.parse import urlparse
from models.database import get_db_session, ScrapingSchedule  # Import session function
from scrapy_project.spiders.spider import Spider  # Import the spider


def get_next_url(db_session):
    """Fetch the next URL that needs scraping based on schedule."""
    url_entry = db_session.query(
        ScrapingSchedule.id,
        func.trim(ScrapingSchedule.url).label("url"),
        ScrapingSchedule.scraped_at,
        ScrapingSchedule.scraping_interval
    ).filter(
        and_(
            ScrapingSchedule.is_active == True,
            (ScrapingSchedule.scraped_at.is_(None)) |
            (ScrapingSchedule.scraped_at + ScrapingSchedule.scraping_interval < datetime.now())
        )
    ).order_by(ScrapingSchedule.scraped_at.asc().nullsfirst()).first()

    return db_session.query(ScrapingSchedule).get(url_entry.id) if url_entry else None

def update_scraped_at(db_session, url_entry):
    """Update the `scraped_at` timestamp after scraping."""
    url_entry.scraped_at = datetime.now()
    db_session.commit()


def run_spider(url_entry):
    """Run the spider for a given URL."""
    parsed_url = urlparse(str(url_entry.url))

    if not parsed_url.scheme:
        print(f"Skipping invalid URL: {url_entry.url}")
        return

    # Extract domain dynamically and pass it to the spider
    allowed_domain = parsed_url.netloc

    process = CrawlerProcess(get_project_settings())
    process.crawl(Spider, start_urls=[url_entry.url.strip()], allowed_domains=[allowed_domain])
    process.start()


if __name__ == "__main__":
    while True:
        db_session = get_db_session()

        try:
            url_entry = get_next_url(db_session)
            if not url_entry:
                print("No URLs to scrape. Exiting...")
                break

            print(f"Scraping: {url_entry.url}")
            run_spider(url_entry)

            update_scraped_at(db_session, url_entry)

        finally:
            db_session.close()
