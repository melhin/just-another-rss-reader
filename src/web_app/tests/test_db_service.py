from datetime import datetime, timedelta
from freezegun import freeze_time

import pytest
import pytest_asyncio

from db.articles import ArticleService, CategoryEnum
from fetcher.feed_models import Entry


@pytest_asyncio.fixture
async def sources(async_db_session):
    article_service = ArticleService(session=async_db_session)
    source1 = await article_service.save_article_source(
        url="url.url.com/url1",
        name="feed1",
        description="feed1 source",
        categories=[CategoryEnum.GENERAL.value, CategoryEnum.TECH.value],
    )
    source2 = await article_service.save_article_source(
        url="url.url.com/url2",
        name="feed2",
        description="feed2 source",
        categories=[CategoryEnum.KERALA.value, CategoryEnum.GENERAL.value],
    )
    return [source1, source2]


@pytest.fixture
def entries():
    test1 = Entry(title="test1", description="test1 description", link="https://test.com/test1")
    test2 = Entry(title="test2", description="test2 description", link="https://test.com/test2")
    return test1, test2


@pytest_asyncio.fixture
async def saved_entries(sources, entries, async_db_session):
    test1, test2 = entries
    source1, source2 = sources
    article_service = ArticleService(session=async_db_session)
    entry1 = await article_service.save_articles(entries=[test1], feed_id=source1)
    entry2 = await article_service.save_articles(entries=[test2], feed_id=source2)
    return entry1[0], entry2[0]


@pytest.mark.asyncio
async def test_retrieval_of_sources(sources, async_db_session):
    article_service = ArticleService(session=async_db_session)
    source1, source2 = sources
    feeds = await article_service.get_all_feeds()
    assert {("url.url.com/url1", source1), ("url.url.com/url2", source2)} == set(feeds)
    # saving a de-active source
    await article_service.save_article_source(
        url="url.url.com/url3",
        name="feed3",
        description="feed3 source",
        active=False,
    )
    # In active feeds are not fetched for collection
    feeds = await article_service.get_all_feeds()
    assert {("url.url.com/url1", source1), ("url.url.com/url2", source2)} == set(feeds)


@pytest.mark.asyncio
async def test_creation_and_retrival_of_article_service(async_db_session, sources, entries):
    article_service = ArticleService(session=async_db_session)
    # Empty entries
    assert await article_service.get_total_articles(when="today") == 0
    test1, test2 = entries
    source1, source2 = sources

    article_service = ArticleService(session=async_db_session)
    await article_service.save_articles(entries=[test1], feed_id=source1)
    await article_service.save_articles(entries=[test2], feed_id=source2)

    assert await article_service.get_total_articles(when="today") == 2
    assert await article_service.get_articles(when="today") == [
        {
            "description": "test2 description",
            "feed": "feed2",
            "title": "test2",
            "url": "https://test.com/test2",
            "categories": ["kerala", "general"],
        },
        {
            "description": "test1 description",
            "feed": "feed1",
            "title": "test1",
            "url": "https://test.com/test1",
            "categories": ["general", "tech"],
        },
    ]


@pytest.mark.asyncio
async def test_adding_multiple_articles(async_db_session, sources, saved_entries):
    article_service = ArticleService(session=async_db_session)
    assert await article_service.get_total_articles(when="today") == 2
    test3 = Entry(title="test3", description="test3 description", link="https://test.com/test3")
    test4 = Entry(title="test4", description="test4 description", link="https://test.com/test4")
    await article_service.save_articles(entries=[test3, test4], feed_id=sources[0])

    assert await article_service.get_total_articles(when="today") == 4


@pytest.mark.asyncio
async def test_existing_articles(async_db_session, saved_entries, entries):
    article_service = ArticleService(session=async_db_session)
    assert await article_service.get_total_articles(when="today") == 2
    assert await article_service.get_existing_links([entries[0].link, entries[1].link]) == [
        entries[0].link,
        entries[1].link,
    ]
    expected = {entries[0].hash: saved_entries[0], entries[1].hash: saved_entries[1]}
    assert await article_service.get_ids_from_hashes([entries[0].hash, entries[1].hash]) == expected


@pytest.mark.asyncio
async def test_pagination(async_db_session, sources, saved_entries):
    article_service = ArticleService(session=async_db_session)
    assert await article_service.get_total_articles(when="today") == 2
    assert await article_service.get_articles(when="today", offset=0, limit=1) == [
        {
            "description": "test2 description",
            "feed": "feed2",
            "title": "test2",
            "url": "https://test.com/test2",
            "categories": ["kerala", "general"],
        }
    ]

    assert await article_service.get_articles(when="today", offset=1, limit=1) == [
        {
            "description": "test1 description",
            "feed": "feed1",
            "title": "test1",
            "url": "https://test.com/test1",
            "categories": ["general", "tech"],
        }
    ]


@pytest.mark.asyncio
@freeze_time("22-12-2022")
async def test_date_filters(async_db_session, sources, saved_entries):
    article_service = ArticleService(session=async_db_session)
    assert await article_service.get_total_articles(when="today") == 2
    test3 = Entry(title="test3", description="test3 description", link="https://test.com/test3")
    test4 = Entry(title="test4", description="test4 description", link="https://test.com/test4")
    created_at = datetime.utcnow() - timedelta(days=2)
    await article_service.save_articles(entries=[test3, test4], feed_id=sources[0], created_at=created_at)

    # No more new articles for today
    assert await article_service.get_total_articles(when="today") == 2
    assert await article_service.get_total_articles(when="thismonth") == 4

    test5 = Entry(title="test5", description="test5 description", link="https://test.com/test5")
    created_at = datetime.utcnow() - timedelta(days=200)
    await article_service.save_articles(entries=[test5], feed_id=sources[0], created_at=created_at)
    # No more new articles last month
    assert await article_service.get_total_articles(when="thismonth") == 4
    assert await article_service.get_total_articles(when="thisyear") == 5

    test6 = Entry(title="test6", description="test6 description", link="https://test.com/test6")
    created_at = datetime.utcnow() - timedelta(days=2000)
    await article_service.save_articles(entries=[test6], feed_id=sources[0], created_at=created_at)
    # No more new articles this year
    assert await article_service.get_total_articles(when="thisyear") == 5


@pytest.mark.asyncio
@freeze_time("22-12-2022")
async def test_category_filters(async_db_session, sources, saved_entries):
    article_service = ArticleService(session=async_db_session)
    assert await article_service.get_total_articles(when="today", category="kerala") == 1
    assert await article_service.get_articles(when="today", category="kerala") == [
        {
            "description": "test2 description",
            "feed": "feed2",
            "title": "test2",
            "url": "https://test.com/test2",
            "categories": ["kerala", "general"],
        },
    ]
    # both the sources have general category
    assert await article_service.get_total_articles(when="today", category="general") == 2
    assert await article_service.get_articles(when="today", category="general") == [
        {
            "description": "test2 description",
            "feed": "feed2",
            "title": "test2",
            "url": "https://test.com/test2",
            "categories": ["kerala", "general"],
        },
        {
            "description": "test1 description",
            "feed": "feed1",
            "title": "test1",
            "url": "https://test.com/test1",
            "categories": ["general", "tech"],
        },
    ]
