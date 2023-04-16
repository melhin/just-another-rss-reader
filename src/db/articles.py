import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy import desc, func, insert, select

from db.models import articles, article_sources, CategoryEnum
from fetcher.feed_models import Entry


class ArticleService:
    def __init__(self, session):
        self.session = session

    async def get_all_feeds(
        self,
    ) -> Tuple[str, str]:
        values = await self.session.execute(
            select([article_sources.c.url, article_sources.c.id])
            .where(article_sources.c.active.is_(True))
            .order_by(desc(article_sources.c.priority))
        )
        return values.fetchall()

    def get_time_slot(self, when: str):
        date_today = datetime.date.today()
        match when:
            case "today":
                return date_today
            case "thisweek":
                return date_today - datetime.timedelta(days=date_today.weekday())
            case "thismonth":
                return date_today.replace(day=1)
            case _:
                return date_today.replace(month=1, day=1)

    async def get_articles(
        self,
        when: str,
        offset: int = 0,
        limit: int = 10,
        category: None | str = None,
    ) -> Dict[str, str]:
        filter = [articles.c.created_at >= self.get_time_slot(when)]
        if category:
            filter.append(article_sources.c.categories.any(category))
        values = await self.session.execute(
            select(
                [
                    articles.c.title,
                    articles.c.url,
                    articles.c.description,
                    article_sources.c.name,
                    article_sources.c.categories,
                ]
            )
            .select_from(articles.join(article_sources))
            .where(*filter)
            .limit(limit)
            .offset(offset)
            .order_by(desc(articles.c.created_at))
        )
        columns = ["title", "url", "description", "feed", "categories"]
        formated_response = [dict(zip(columns, row)) for row in values.fetchall()]
        return formated_response

    async def get_total_articles(
        self,
        when: str,
        category: None | str = None,
    ) -> int:
        filter = [articles.c.created_at >= self.get_time_slot(when)]
        if category:
            filter.append(article_sources.c.categories.any(category))
        response = await self.session.execute(
            select(func.count(articles.c.id)).select_from(articles).join(article_sources).where(*filter)
        )
        return response.scalar_one()

    async def get_ids_from_hashes(self, hashes: List[str]) -> Dict[str, str]:
        values = await self.session.execute(select([articles.c.hash, articles.c.id]).where(articles.c.hash.in_(hashes)))
        return {ele[0]: ele[1] for ele in values.fetchall()}

    async def get_existing_links(self, links: List[str]) -> List[str]:
        values = await self.session.execute(select([articles.c.url]).where(articles.c.url.in_(links)))
        return [r[0] for r in values.fetchall()]

    async def save_article_source(
        self,
        url: str,
        name: str,
        description: str,
        categories: Optional[CategoryEnum] = [],
        active: bool = True,
    ):
        saved = await self.session.execute(
            insert(article_sources).values(
                url=url,
                name=name,
                description=description,
                created_at=datetime.datetime.utcnow(),
                active=active,
                categories=categories,
            )
        )
        return saved.inserted_primary_key[0]

    async def save_articles(self, entries: Entry, feed_id: int, created_at=None):
        created_at = created_at if created_at else datetime.datetime.utcnow()
        records = []
        saved_pks = []
        for entry in entries:
            records.append(
                {
                    "hash": entry.hash,
                    "url": entry.link,
                    "title": entry.title,
                    "description": entry.description,
                    "article_source_id": feed_id,
                    "created_at": created_at,
                }
            )
        if records:
            saved = await self.session.execute(insert(articles), records)
            saved_pks = [ele[0] for ele in saved.inserted_primary_key_rows]

        return saved_pks
