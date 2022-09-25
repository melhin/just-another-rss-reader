import logging
import sqlite3
import os
from contextlib import asynccontextmanager
from pathlib import Path
from databases import Database
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base


import aiosqlite

logger = logging.getLogger(__name__)


print("Calling database")

DB_URL = "postgresql+asyncpg://postgres:postgres@localhost/another-reader"
database = Database(DB_URL)
metadata = MetaData()


def get_db_path() -> Path:
    default_storage = Path.cwd() / "storage"
    storage_path = os.getenv("STORAGE_PATH", default_storage)
    return os.path.join(storage_path, "db.sqlite3")


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
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_articles
                    FOREIGN KEY (article_id)
                    REFERENCES article(id)
            )
        """
        )
        conn.commit()
