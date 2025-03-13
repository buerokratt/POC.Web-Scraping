"""Parsing functions for BeautifulSoup."""


from bs4 import BeautifulSoup
from typing import List, Tuple

def parse_javascript_links(page):
    """Extract all links dynamically generated on the current page."""
    return page.eval_on_selector_all('a', 'elements => elements.map(el => el.href)')


def parse_html_links(html_content):
    """Parse HTML content and extract all links."""
    soup = BeautifulSoup(html_content, 'lxml')
    links = [a['href'] for a in soup.find_all('a', href=True)]

    return links


def parse_html_paragraphs(html_content):
    """Parse HTML content and extract all paragraphs."""
    soup = BeautifulSoup(html_content, 'lxml')
    paragraphs = [p.get_text() for p in soup.find_all('p')]

    return paragraphs


def parse_html_images(html_content):
    """Parse HTML content and extract all image sources."""
    soup = BeautifulSoup(html_content, 'lxml')
    images = [img['src'] for img in soup.find_all('img', src=True)]

    return images


def parse_html_titles_and_contents(html_content) -> List[Tuple[str, str]]:
    soup = BeautifulSoup(html_content, 'lxml')
    titles = []
    current_title = None
    content = []

    for tag in soup.find_all(['h1', 'h2', 'p']):
        if tag.name in ['h1', 'h2']:
            if current_title and content:
                titles.append((current_title, ' '.join(content)))
            current_title = tag.get_text(strip=True)
            content = []
        elif tag.name == 'p':
            content.append(tag.get_text(strip=True))

    if current_title and content:
        titles.append((current_title, ' '.join(content)))

    return titles
