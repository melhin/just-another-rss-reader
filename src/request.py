import httpx

GLOBAL_TIMEOUT = 30


async def fetch_from_url(url: str, timeout=GLOBAL_TIMEOUT):
    async with httpx.AsyncClient() as client:
        return await client.get(url, timeout=timeout)
