import logging
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

import aiosqlite

logger = logging.getLogger(__name__)


def get_db_path() -> Path:
    here = Path.cwd()
    while not (here / ".git").exists():
        if here == here.parent:
            raise RuntimeError("Cannot find root github dir")
        here = here.parent

    return here / "db.sqlite3"


@asynccontextmanager
async def connection():
    sqlite_db = get_db_path()
    db = await aiosqlite.connect(sqlite_db)
    try:
        yield db
    finally:
        await db.close()


def try_make_db() -> None:
    logger.info("Initializing table creation")
    sqlite_db = get_db_path()

    with sqlite3.connect(sqlite_db) as conn:
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                description TEXT,
                feed_url TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS article_keywords (
                keyword TEXT,
                article_id INTEGER NOT NULL,
                CONSTRAINT fk_articles
                    FOREIGN KEY (article_id)
                    REFERENCES article(id)
            )
        """
        )
        conn.commit()
