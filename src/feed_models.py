from typing import List

from pydantic import BaseModel


class Entry(BaseModel):
    title: str
    description: str
    entities: List[str]
    link: str


class Feed(BaseModel):
    entries: List[Entry]
    source: str


class CompleteData(BaseModel):
    feeds: List[Feed] = []


class FeedParserResponse(BaseModel):
    link: str
    title: str
