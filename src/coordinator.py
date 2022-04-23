import pickle

from src.feed_models import CompleteData
from src.fetch import fetch_feed


def save_pickle(complete_data: CompleteData, filename: str):
    with open(filename, "wb") as fh:
        pickle.dump(complete_data, fh, protocol=pickle.HIGHEST_PROTOCOL)


async def start_collection(feed_file: str):
    with open(feed_file) as fh:
        data = fh.readlines()
    complete_data = await fetch_feed(data)
    save_pickle(complete_data, filename="new_data.pkl")
