from datetime import datetime

import requests
from bs4 import BeautifulSoup
import json

# Request the page content
url = "http://example.com"  # Replace with your target URL
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# The idea is to parse all of the data either like this or "slowly" instead, so that under each title would be its paragraphs,
# could maybe also add a list of the links on page
# Extract data
title = soup.find("h1").get_text() if soup.find("h1") else None
content = " ".join([p.get_text() for p in soup.find_all("p")])
publish = soup.find("time").get_text() if soup.find("time") else None
date = datetime.now()
links = [a['href'] for a in soup.find_all('a', href=True)]

# TODO: convert to json from object?
# Should be possible

# Structure the data
data = {
    "document_id": "top level url",
    "title": title,     # h1
    "content": content, # p
    "links": links,     # a
    "images": images,   # img source links -> maybe download the image and add later?
    "metadata": {
        "date_published": publish,  # page published date
        "fate_parsed": date,        # when parse
        "url" : url                 # page itself
    }
}

# Save to JSON file
with open(url + ".json", "w") as json_file:
    json.dump(data, json_file, indent=4)
