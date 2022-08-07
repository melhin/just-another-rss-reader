import asyncio
import logging
from typing import List

import feedparser

from src.db import connection
from src.db.articles import Article
from src.fetcher.feed_models import CompleteData, Feed, FeedParserResponse
from src.fetcher.request import fetch_from_url
from src.fetcher.text_process import get_entry

logger = logging.getLogger(__name__)
SIMULTANEOUS_DOWNLOADS = 5


async def get_links_from_feed(feed_url: str) -> List[FeedParserResponse]:
    response = await fetch_from_url(url=feed_url)
    feed_parser_responses = []
    for entry in feedparser.parse(response.text).entries:
        feed_parser_responses.append(
            FeedParserResponse(link=entry.link, title=entry.title, feed_url=feed_url)
        )
    return feed_parser_responses


async def safe_get_entry(sem, feed_parser_response):
    async with sem:  # semaphore limits num of simultaneous downloads
        return await get_entry(feed_parser_response)


async def fetch_feed(data) -> CompleteData:
    complete_data = CompleteData()
    article = Article()
    for feed in data:
        async with connection() as db_conn:
            try:
                feed = feed.strip()
                entries = []
                logger.info("Collecting values from %s", feed)
                feed_parser_responses = await get_links_from_feed(feed)
                all_links = [ele.link for ele in feed_parser_responses]
                existing_link = await article.get_existing_links(
                    connection=db_conn,
                    links=all_links,
                )
                sem = asyncio.Semaphore(SIMULTANEOUS_DOWNLOADS)
                tasks = [
                    # creating task starts coroutine
                    asyncio.ensure_future(safe_get_entry(sem, feed_parser_response))
                    for feed_parser_response in feed_parser_responses
                    if feed_parser_response.link not in existing_link
                ]
                entries = await asyncio.gather(*tasks, return_exceptions=False)
                await article.save_articles(
                    connection=db_conn, entries=entries, feed_url=feed
                )
            except Exception as ex:
                logger.error("Caught error executing task %s", ex)
                raise ex
