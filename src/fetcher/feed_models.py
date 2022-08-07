from hashlib import md5
from typing import List

from pydantic import BaseModel


class Entry(BaseModel):
    title: str
    description: str
    entities: List[str]
    link: str

    @property
    def hash(self):
        return md5(self.link.encode("utf-8")).hexdigest()


class Feed(BaseModel):
    entries: List[Entry]
    source: str


class CompleteData(BaseModel):
    feeds: List[Feed] = []


class FeedParserResponse(BaseModel):
    link: str
    title: str
    feed_url: str
