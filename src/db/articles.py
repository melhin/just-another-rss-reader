from collections import defaultdict
from typing import Dict, List

from aiosqlite import Connection
from src.feed_models import Entry


class Article:
    async def get_existing_links(
        self, connection: Connection, links: List[str]
    ) -> List[str]:
        cursor = await connection.cursor()
        sql = f"SELECT  url  FROM articles where url in ({','.join(['?']*len(links))})"
        await cursor.execute(sql, links)
        response = [ele[0] for ele in await cursor.fetchall()]
        await cursor.close()
        return response

    async def get_ids_from_hashes(
        self, connection: Connection, hashes: List[str]
    ) -> Dict[str, str]:
        cursor = await connection.cursor()
        sql = f"SELECT  hash, id  FROM articles where hash in ({','.join(['?']*len(hashes))})"
        await cursor.execute(sql, hashes)
        response = {ele[0]: ele[1] for ele in await cursor.fetchall()}
        await cursor.close()
        return response

    async def save_articles(
        self, connection: Connection, entries: Entry, feed_url: str
    ):
        cursor = await connection.cursor()
        records = []
        entities = defaultdict(list)
        for entry in entries:
            records.append(
                (entry.hash, entry.link, entry.title, entry.description, feed_url)
            )
            entities[entry.hash] = entry.entities
        await cursor.executemany(
            "insert into articles(hash, url, title, description, feed_url) values(?,?,?,?,?)",
            records,
        )
        await connection.commit()

        hash_id_mapping = await self.get_ids_from_hashes(
            connection, list(entities.keys())
        )
        for hash, keywords in entities.items():
            records = [(keyword, hash_id_mapping[hash]) for keyword in keywords]
            await cursor.executemany(
                "insert into article_keywords(keyword, article_id) values(?,?)", records
            )
            await connection.commit()

        await cursor.close()
