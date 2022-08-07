from src.db import try_make_db
from src.fetcher.fetch import fetch_feed


async def start_collection(feed_file: str):
    try_make_db()
    with open(feed_file) as fh:
        data = fh.readlines()
    await fetch_feed(data)
