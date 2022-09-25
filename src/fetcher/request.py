import httpx

GLOBAL_TIMEOUT = 30


async def fetch_from_url(url: str, timeout=GLOBAL_TIMEOUT):
    async with httpx.AsyncClient() as client:
        client.headers['User-Agent'] = 'Custom Bot'
        return await client.get(url, timeout=timeout)
