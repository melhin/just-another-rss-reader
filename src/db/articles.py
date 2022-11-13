import datetime
from typing import Dict, List, Tuple
from collections import defaultdict

from sqlalchemy import desc, func, insert, select

from db.models import articles, article_sources, article_keywords
from fetcher.feed_models import Entry


class ArticleService:
    def __init__(self, session):
        self.session = session

    async def get_all_feeds(
        self,
    ) -> Tuple[str, str]:
        values = await self.session.execute(
            select([article_sources.c.url, article_sources.c.id]).order_by(desc(article_sources.c.priority))
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
    ) -> Dict[str, str]:
        values = await self.session.execute(
            select([articles.c.title, articles.c.url, articles.c.description, article_sources.c.name])
            .select_from(articles.join(article_sources))
            .where(articles.c.created_at >= self.get_time_slot(when))
            .limit(limit)
            .offset(offset)
            .order_by(desc(articles.c.created_at))
        )
        columns = ["title", "url", "description", "feed"]
        formated_response = [dict(zip(columns, row)) for row in values.fetchall()]
        return formated_response

    async def get_total_articles(self, when: str) -> int:
        response = await self.session.execute(
            select([func.count()]).select_from(articles).where(articles.c.created_at >= self.get_time_slot(when))
        )
        return response.scalar()

    async def get_ids_from_hashes(self, hashes: List[str]) -> Dict[str, str]:
        values = await self.session.execute(select([articles.c.hash, articles.c.id]).where(articles.c.hash.in_(hashes)))
        return {ele[0]: ele[1] for ele in values.fetchall()}

    async def get_existing_links(self, links: List[str]) -> List[str]:
        values = await self.session.execute(select([articles.c.url]).where(articles.c.url.in_(links)))
        return [r[0] for r in values.fetchall()]

    async def save_article_source(self, url: str, name: str, description: str):
        saved = await self.session.execute(
            insert(article_sources).values(
                url=url, name=name, description=description, created_at=datetime.datetime.utcnow()
            )
        )
        return saved.inserted_primary_key[0]

    async def save_articles(self, entries: Entry, feed_id: int, created_at=None):
        created_at = created_at if created_at else datetime.datetime.utcnow()
        records = []
        saved_pks = []
        entities = defaultdict(list)
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
            entities[entry.hash] = entry.entities
        if records:
            saved = await self.session.execute(insert(articles), records)
            saved_pks = [ele[0] for ele in saved.inserted_primary_key_rows]

        hash_id_mapping = await self.get_ids_from_hashes(list(entities.keys()))
        for hash, keywords in entities.items():
            keyword_records = [
                {"keyword": keyword, "article_id": hash_id_mapping[hash], "created_at": created_at}
                for keyword in keywords
            ]
            if keyword_records:
                await self.session.execute(insert(article_keywords), keyword_records)
        return saved_pks
