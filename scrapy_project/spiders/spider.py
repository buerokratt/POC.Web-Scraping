"""Main spider class."""


import re

import os
import time
import asyncio
from urllib.parse import urljoin, urlparse
from datetime import datetime
import scrapy
import base64
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from scrapy.utils.project import get_project_settings
from models.database import LinkMetadata
from utils.parsing_utils import parse_html_links


class Spider(scrapy.Spider):
    """Spider class."""
    name = "example_spider"

    def __init__(self, *args, start_urls=None, **kwargs):
        """
        Initialize the spider.

        Args:
            start_urls (list, optional): List of start URLs for the spider.
        """
        super().__init__(*args, **kwargs)
        self.start_time = time.time()
        self.start_urls = start_urls or []
        self.visited_links = set()
        self.allowed_domains = [self._normalize_domain(urlparse(self.start_urls[0]).netloc)] \
            if self.start_urls else [
            ""]
        self.output_file = f"{self.allowed_domains[0]}_data.json"

    def parse(self, response):
        """
        Main parse method to handle the response and process links.

        Args:
            response (scrapy.http.Response): Response object from the request.

        Yields:
            scrapy.Request: New requests for further crawling.
        """
        url = response.url

        self.logger.info(f"Parsing {url}")

        # Detect language
        if self.check_for_pdf(response):
            self.save_pdf(response)
            return
        else:
            language = self.detect_language(response)

        # Get response metadata
        status_code = response.status
        last_modified = response.headers.get('Last-Modified', b'').decode('utf-8')

        # Save metadata to database
        self.save_metadata_to_db(
            url=url,
            language=language,
            last_modified_at=last_modified,
            status_code=status_code,
        )

        # Check if the URL should be skipped based on file types
        if (not url.endswith(".pdf") and not url.endswith(".docx")
                and not self.check_for_pdf(response)):
            if self.requires_javascript(response):
                yield from self.scrape_with_playwright(response)
            else:
                yield from self.scrape_with_beautifulsoup(response)
        else:
            yield from self.scrape_with_beautifulsoup(response)

    def save_pdf(self, response):
        """
        Save PDF file from the response using the same logic as HTML files.
        Args:
            response (scrapy.http.Response): Response object from the request.
        """
        url = response.url
        folder_name = self._normalize_domain(urlparse(url).netloc)
        encoded_file_name = self.encode_url(urlparse(url).path) + ".pdf"  # Encode URL for filename

        current_directory = os.getcwd()
        folder_path = os.path.join(current_directory, "data", folder_name)


        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_path = os.path.join(folder_path, encoded_file_name)

        with open(file_path, 'wb') as file:
            file.write(response.body)  # Save raw PDF content as bytes

        self.logger.info(f"Saved PDF file: {file_path}")

    def save_metadata_to_db(self, url, language, last_modified_at, status_code):
        """
        Save link metadata to the database, updating it if it already exists.

        Args:
            url (str): The URL of the page.
            language (str): Detected language of the page.
            last_modified_at (str): Last modified timestamp of the page.
            status_code (int): HTTP status code of the response.
        """
        # Only save metadata if the language is "et" or "unknown"
        if language not in ("et", "unknown"):
            self.logger.info(f"Skipping metadata save for URL: {url} due to language: {language}")
            return

        session_factory = get_project_settings().get("DB_SESSION_FACTORY")
        if session_factory is None:
            self.logger.error("DB_SESSION_FACTORY is not configured in settings.")
            return

        session = session_factory()  # Dynamically fetch the session
        try:
            # Check if the metadata already exists based on the unique URL
            existing_metadata = session.query(LinkMetadata).filter_by(url=url).first()
            if existing_metadata:
                # Update the existing record
                existing_metadata.language = language
                existing_metadata.last_modified_at = last_modified_at or None
                existing_metadata.status_code = status_code
                existing_metadata.scraped_at = datetime.now()  # Update the scraped timestamp
                self.logger.info(f"Updated metadata for URL: {url}")
            else:
                # Insert a new record
                metadata = LinkMetadata(
                    url=url,
                    language=language,
                    last_modified_at=last_modified_at or None,
                    status_code=status_code,
                    scraped_at=datetime.now(),  # Add the current UTC time
                )
                session.add(metadata)
                self.logger.info(f"Saved metadata for URL: {url}")

            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to save metadata for URL: {url}, Error: {e}")
        finally:
            session.close()

    def detect_language(self, response):
        """
        Detect the language of the response content.

        Args:
            response (scrapy.http.Response): Response object from the request.

        Returns:
            str: Detected language code (e.g., "en", "et", or "unknown").
        """
        # Look for the language in the HTML content
        soup = BeautifulSoup(response.text, "html.parser")
        html_tag = soup.find("html")
        if html_tag and html_tag.get("lang"):
            return html_tag["lang"].split("-")[0]

        # Return unknown if no language is detected
        return "unknown"

    def requires_javascript(self, response):
        """
        Determine if a page requires JavaScript rendering.

        Args:
            response (scrapy.http.Response): Response object from the request.

        Returns:
            bool: True if JavaScript rendering is needed, False otherwise.
        """
        content = response.text.lower()
        js_frameworks = ["react", "angular", "vue", "next.js", "svelte"]
        if any(framework in content for framework in js_frameworks):
            return True
        dynamic_indicators = ["<script", "spinner", "loading", "aria-busy"]
        if any(indicator in content for indicator in dynamic_indicators):
            return True
        return False

    async def scrape_with_playwright_async(self, url):
        """
        Scrape and render JavaScript-heavy pages asynchronously.

        Args:
            url (str): URL to scrape.

        Returns:
            str: Rendered HTML content of the page.
        """
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded")

            # Scroll and wait for content to load
            for _ in range(5):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)  # Use asyncio-compatible sleep

            # Extract content after rendering
            content = await page.content()
            await browser.close()
            return content  # Return the rendered content

    def scrape_with_playwright(self, response):
        """
        Wrapper for asynchronous Playwright scraping to integrate with Scrapy.

        Args:
            response (scrapy.http.Response): Response object from the request.

        Yields:
            scrapy.Request: New requests for further crawling.
        """
        url = response.url
        content = asyncio.run(self.scrape_with_playwright_async(url))
        self.save_content(content, response)
        # Extract links dynamically for further crawling
        links = parse_html_links(content)

        for link in links:
            full_link = urljoin(url, link)
            if self.is_valid_url(full_link):
                yield response.follow(full_link, self.parse)

    def scrape_with_beautifulsoup(self, response):
        """
        Scrape static pages using BeautifulSoup.

        Args:
            response (scrapy.http.Response): Response object from the request.

        Yields:
            scrapy.Request: New requests for further crawling.
        """
        soup = BeautifulSoup(response.body, "html.parser")
        self.save_content(soup.prettify(), response)
        links = parse_html_links(response.body)

        # Filter and follow valid links for further scraping
        self.logger.info(f"Found {len(links)} links on {response.url}")
        for link in links:
            full_link = urljoin(response.url, link)
            if self.is_valid_url(full_link):
                yield response.follow(full_link, self.parse)

    def save_content(self, content, response):
        """
        Save page content to a file.

        Args:
            content (str): Content of the page.
            response (scrapy.http.Response): Response object from the request.
        """
        url = response.url

        if not self.ignore_xml(url):
            folder_name = self._normalize_domain(urlparse(url).netloc)
            parsed_link = urlparse(url)
            output_file = ""

            # if url.endswith(".pdf") or self.check_for_pdf(response):
            #     output_file = parsed_link.path + ".pdf"
            if url.endswith(".docx"):
                output_file = parsed_link.path + ".docx"
            elif url.endswith(".doc"):
                output_file = parsed_link.path + ".doc"
            elif not self.ignore_language(content):
                output_file = parsed_link.path  # No encoding yet
                encoded_file_name = self.encode_url(output_file) + ".html"  # Apply encoding once
                self.create_folder_and_file(folder_name, encoded_file_name, content)

            self.logger.info(f"Saved file: {output_file}")

    def create_folder_and_file(self, folder_name, file_name, file_content):
        """
        Create a folder and save content to a file.

        Args:
            folder_name (str): Name of the folder.
            file_name (str): Name of the file.
            file_content (str): Content to save in the file.
        """
        current_directory = os.getcwd()
        folder_path = os.path.join(current_directory, "data", folder_name)


        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_path = os.path.join(folder_path, file_name)

        with open(file_path, 'w', encoding="utf-8") as file:
            file.write(file_content)

    def encode_url(self, url):
        """
        Encodes the URL in base64 format for safe file storage.

        Args:
            url (str): The original URL.

        Returns:
            str: Base64 encoded string without padding (=).
        """
        encoded = base64.urlsafe_b64encode(url.encode()).decode()
        return encoded.rstrip("=")  # Remove padding characters to keep it clean

    def _normalize_domain(self, domain):
        """
        Normalize the domain name for folder structure.

        Args:
            domain (str): Domain name to normalize.

        Returns:
            str: Normalized domain name.
        """
        return domain.lower().lstrip("www.").rstrip("/")

    def ignore_language(self, content):
        """
        Check if the page should be ignored based on its language.

        Args:
            content (str): HTML content of the page.

        Returns:
            bool: True if the language is to be ignored, False otherwise.
        """
        if 'lang="et"' in content:
            return False
        if 'lang="en"' in content or 'lang="ru"' in content or 'lang="en-US"' in content:
            return True
        return False

    def ignore_xml(self, url):
        """
        Check if the URL points to an XML file.

        Args:
            url (str): URL to check.

        Returns:
            bool: True if the URL ends with .xml, False otherwise.
        """
        return url.lower().endswith(".xml")

    def is_valid_url(self, url):
        """
        Check if the URL is valid and belongs to the allowed domain.

        Args:
            url (str): URL to validate.

        Returns:
            bool: True if the URL is valid, False otherwise.
        """
        parsed = urlparse(url)

        # Matches '/ru/' or '/en/' in the URL path
        language_pattern = re.compile(r"/(?:ru|en)/")
        # Matches 'uudised' or 'uudis' or 'news' anywhere in the path
        news_pattern = re.compile(r"uudis(ed)?|news")

        # Check if the URL path matches any of the patterns
        if language_pattern.search(parsed.path.lower()) or news_pattern.search(parsed.path.lower()):
            return False

        if (parsed.scheme not in ('http', 'https')
                or self._normalize_domain(parsed.netloc) != self.allowed_domains[0]):
            return False

        return True

    def check_for_pdf(self, response):
        """
        Check if the response is a PDF based on the Content-Type header.

        Args:
            response (scrapy.http.Response): Response object from the request.

        Returns:
            bool: True if the response is a PDF, False otherwise.
        """
        content_type = response.headers.get('Content-Type', b'').decode('utf-8')
        if 'application/pdf' in content_type:
            return True  # Indicate that this is a PDF and no further processing is needed
        return False
