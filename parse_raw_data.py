import os
import logging
from datetime import datetime
from models.database import get_db_session, LinkMetadata
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

RAW_DATA_DIR = os.getenv("RAW_DATA_DIR", "/app/data")


def parse_html_to_json(file_path, base_url):
    """Parses raw HTML file into structured JSON."""
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    parsed_data = {
        "url": base_url,
        "title": soup.title.string if soup.title else "",
        "content": []
    }

    current_section = None
    for element in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p"]):
        if element.name.startswith("h"):
            current_section = {"header": element.get_text(strip=True), "paragraphs": []}
            parsed_data["content"].append(current_section)
        elif element.name == "p" and current_section:
            current_section["paragraphs"].append(element.get_text(strip=True))

    return parsed_data


def process_files(raw_data_dir):
    """Processes all raw HTML files, converts them to JSON, and saves them."""
    session = get_db_session()

    if not os.path.exists(raw_data_dir) or not os.listdir(raw_data_dir):
        logging.info(f"No HTML files found in {raw_data_dir}. Exiting.")
        return

    for filename in os.listdir(raw_data_dir):
        if not filename.endswith(".html"):
            continue

        file_path = os.path.join(raw_data_dir, filename)
        logging.info(f"Processing file: {file_path}")  # Log file being processed

        try:
            url = extract_url_from_filename(filename, raw_data_dir)
            logging.info(f"Decoded URL: {url}")
        except Exception as e:
            logging.error(f"Error decoding {filename}: {e}")
            continue

        parsed_json = parse_html_to_json(file_path, url)

        metadata_entry = session.query(LinkMetadata).filter_by(url=url).first()
        if metadata_entry:
            metadata_entry.parsed_at = datetime.now()
            metadata_entry.parsed_data = parsed_json  # Save JSON directly instead of dumping as a string
            metadata_entry.status_code = metadata_entry.status_code or 200  # Ensure status code is stored
            logging.info(f"Updated existing entry: {url}")
        else:
            metadata_entry = LinkMetadata(
                url=url,
                parsed_at=datetime.now(),
                parsed_data=parsed_json,  # Save JSON directly
                status_code=200  # Default status code if missing
            )
            session.add(metadata_entry)
            logging.info(f"Created new entry: {url}")

        try:
            session.commit()
            logging.info(f"Successfully saved to database: {url}")
        except Exception as e:
            session.rollback()
            logging.error(f"Database commit failed for {url}: {e}")

    session.close()


def process_all_raw_data():
    """Iterates over all directories inside RAW_DATA_DIR and processes each."""
    if not os.path.exists(RAW_DATA_DIR):
        logging.error(f"RAW_DATA_DIR {RAW_DATA_DIR} does not exist.")
        return

    for site_dir in os.listdir(RAW_DATA_DIR):
        site_path = os.path.join(RAW_DATA_DIR, site_dir)
        if os.path.isdir(site_path):
            logging.info(f"Processing site: {site_dir}")
            process_files(site_path)


def extract_url_from_filename(filename, base_dir):
    """Decodes the filename from Base64 to get the original URL and ensures full domain."""
    import base64
    filename = filename.replace(".html", "")
    padding_needed = len(filename) % 4
    if padding_needed:
        filename += "=" * (4 - padding_needed)
    try:
        decoded_bytes = base64.urlsafe_b64decode(filename)
        decoded_url = decoded_bytes.decode("utf-8")
    except Exception as e:
        raise ValueError(f"Base64 decoding failed for {filename}: {e}")

    domain = os.path.basename(base_dir)  # Get the domain from the directory name
    parsed_url = urlparse(decoded_url)

    if not parsed_url.scheme:
        decoded_url = f"https://www.{domain}{decoded_url}"  # Ensure full URL structure

    return decoded_url


if __name__ == "__main__":
    logging.info("Starting parser...")
    process_all_raw_data()
    logging.info("Parsing completed.")
