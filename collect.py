import asyncio
import logging
import sys

from src.fetcher.coordinator import start_collection


logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    asyncio.run(start_collection(sys.argv[1]))
