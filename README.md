# RIA Project

This repository contains a Scrapy-based web scraping project designed for extracting and storing data from specified websites. It uses Python's Scrapy framework, BeautifulSoup for parsing HTML, and SQLAlchemy for database interaction. The project is containerized using Docker.


## Features

- **Scrapy Framework**: Core web scraping capabilities.
- **HTML Parsing**: Uses BeautifulSoup for efficient parsing.
- **Database Support**: Stores metadata using SQLAlchemy and PostgreSQL.
- **Dynamic Crawling**: Filters and processes links dynamically.
- **Dynamic Content Handling**: Using Playwright to scrape JavaScript-rendered content.
- **Dockerized Setup**: Easy deployment using Docker and Docker Compose.

---

## Project Structure

```plaintext
ria-projekt
├── config/                      # Configuration files
│   └── app_config.py            # Project-wide settings
├── models/                      # Data models
│   ├── database.py              # Database setup and models
│   └── scraped_data.py          # Data serialization models
├── scrapy_project/              # Scrapy project
│   ├── spiders/                 # Scrapy spider
│   │   ├── spider.py            # Main spider class
│   │   └── settings.py          # Scrapy settings
├── test/                        # Tests
├── utils/                       # Utility scripts
│   ├── parsing_utils.py         # Parsing helpers
│   └── test_parse.py            # Test parsing
└── Dockerfile                   # Docker image definition
└── docker-compose.yml           # Multi-container Docker setup
└── Pipfile                      # Pipfile with requirements
└── Pipfile.lock                 # Pipfile.lock
```

---

## Setup and Installation

### Prerequisites

- Python 3.13 or higher
- PostgreSQL
- Docker and Docker Compose

### Installation Steps

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd ria-projekt
   ```

2. Install dependencies:

   ? #TODO

3. Connect Database:

4. Build and run Docker containers:

   ```bash
   docker-compose build
   ```

   ```bash
   docker-compose up
   ```

---

## Usage

### Running the Spider

Runs by itself when typing 

   ```bash
   docker-compose up
   ```

### Output

Scraped data will be saved to new (or already existing) directory with the same name as master domain or scraped page.

---

## Configuration

### Scrapy Settings

Modify settings in `scrapy_project/settings.py`. For example:

- **USER\_AGENT**: Define the user agent.
- **CONCURRENT\_REQUESTS**: Control concurrency.
- **FEEDS**: Customize the output format and file.

### Database Configuration

Update the following environment variables:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_DB`


