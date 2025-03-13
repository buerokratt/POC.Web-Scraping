import json
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class Metadata:
    date_published: Optional[str]
    date_parsed: str
    url: str

    def to_dict(self):
        return {
            "date_published": self.date_published,
            "date_parsed": self.date_parsed,
            "url": self.url
        }

@dataclass
class TitleData:
    title_name: str
    content: str
    links: List[str]
    images: List[str]
    metadata: Metadata

    def to_dict(self):
        return {
            "title_name": self.title_name,
            "content": self.content,
            "links": self.links,
            "images": self.images,
            "metadata": self.metadata.to_dict()
        }

@dataclass
class ScrapedData:
    document_id: str
    titles: List[TitleData] = field(default_factory=list)

    def to_dict(self):
        return {
            "document_id": self.document_id,
            "titles": [title.to_dict() for title in self.titles]
        }

    def save_to_json(self, filepath: str):
        with open(filepath, 'w') as json_file:
            json.dump(self.to_dict(), json_file, indent=4)
