import logging
from typing import List

import nltk
import spacy
from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.html import HtmlParser
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.utils import get_stop_words

from src.feed_models import Entry, FeedParserResponse
from src.request import fetch_from_url

LANGUAGE = "english"
SENTENCES_COUNT = 10

logger = logging.getLogger(__name__)
nlp = spacy.load("en_core_web_sm")


def generate_article_summary(body: str, url: str) -> str:
    parser = HtmlParser.from_string(body, url, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    sentences = ""
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        sentences += f". {sentence}"
    return sentences


def get_entities_for_text(entry: Entry) -> List[str]:
    logging.info("Got for analysis in worker %s", entry.title)
    allowed_lables = ["GPE", "NORP", "PERSON", "LOC", "ORG"]
    doc = nlp(entry.description)
    entities = set()
    for ent in doc.ents:
        if ent.label_ in allowed_lables:
            entities.add(ent.text)
    logging.info("Finished analysis in worker %s", entry.title)
    return entities


async def get_entry(feed_parser_response: FeedParserResponse) -> Entry:
    logger.info("Fetching article with title %s", feed_parser_response.title)
    entry = Entry(
        title=feed_parser_response.title,
        link=feed_parser_response.link,
        description="",
        entities=[],
    )
    try:
        body = await fetch_from_url(feed_parser_response.link)
        entry.description = generate_article_summary(body.text, entry.link)
        entry.entities = get_entities_for_text(entry)
    except Exception as e:
        logger.error("Parsing %s failed with %s", entry.title, e)
    return entry
