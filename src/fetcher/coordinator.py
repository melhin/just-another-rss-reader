from src.fetcher.fetch import fetch_feed


async def start_collection():
    await fetch_feed()
