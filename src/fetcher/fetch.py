import asyncio
import logging
from typing import List

import feedparser

from db.articles import ArticleService
from fetcher.feed_models import CompleteData, FeedParserResponse
from fetcher.request import fetch_from_url
from db.session import get_db_session
from fetcher.text_process import get_entry

logger = logging.getLogger(__name__)
SIMULTANEOUS_DOWNLOADS = 5


async def get_links_from_feed(feed_url: str) -> List[FeedParserResponse]:
    response = await fetch_from_url(url=feed_url)
    feed_parser_responses = []
    for entry in feedparser.parse(response.text).entries:
        feed_parser_responses.append(FeedParserResponse(link=entry.link, title=entry.title, feed_url=feed_url))
    return feed_parser_responses


async def safe_get_entry(sem, feed_parser_response):
    async with sem:  # semaphore limits num of simultaneous downloads
        return await get_entry(feed_parser_response)


async def fetch_feed() -> CompleteData:
    async with get_db_session() as session:
        article_service = ArticleService(session=session)
        for feed_url, feed_id in await article_service.get_all_feeds():
            try:
                feed = feed_url.strip()
                entries = []
                logger.info("Collecting values from %s", feed)
                feed_parser_responses = await get_links_from_feed(feed)
                all_links = [ele.link for ele in feed_parser_responses]
                existing_link = await article_service.get_existing_links(
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
                await article_service.save_articles(entries=entries, feed_id=feed_id)
            except Exception as ex:
                logger.error("Caught error executing task %s", ex)
                raise ex
