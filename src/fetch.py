import asyncio
import logging
from typing import List

import feedparser

from src.feed_models import CompleteData, Feed, FeedParserResponse
from src.request import fetch_from_url
from src.text_process import get_entry

logger = logging.getLogger(__name__)
SIMULTANEOUS_DOWNLOADS = 5


async def get_links_from_feed(feed_url: str) -> List[FeedParserResponse]:
    response = await fetch_from_url(url=feed_url)
    return feedparser.parse(response.text).entries


async def safe_get_entry(sem, link):
    async with sem:  # semaphore limits num of simultaneous downloads
        return await get_entry(link)


async def fetch_feed(data) -> CompleteData:
    complete_data = CompleteData()
    for feed in data:
        feed = feed.strip()
        feed_data = []
        logger.info("Collecting values from %s", feed)
        links = await get_links_from_feed(feed)
        sem = asyncio.Semaphore(SIMULTANEOUS_DOWNLOADS)
        try:
            tasks = [
                # creating task starts coroutine
                asyncio.ensure_future(safe_get_entry(sem, link))
                for link in links
            ]
            feed_data = await asyncio.gather(*tasks, return_exceptions=False)
        except Exception as ex:
            logger.error("Caught error executing task %s", ex)
        complete_data.feeds.append(Feed(source=feed, entries=feed_data))
    return complete_data
