from db.models import articles
import factory
from fetcher.feed_models import Entry
from db.articles import ArticleService


class ArticleFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = articles
        sqlalchemy_session_persistence = "commit"


async def create_articles(session):

    test1 = Entry(
        title="test1", description="test1 description", entities=["test1", "description"], link="https://test.com/test1"
    )
    test2 = Entry(
        title="test2", description="test2 description", entities=["test2", "description"], link="https://test.com/test2"
    )
    test3 = Entry(
        title="test3", description="test3 description", entities=["test3", "description"], link="https://test.com/test3"
    )
    test4 = Entry(
        title="test4", description="test4 description", entities=["test4", "description"], link="https://test.com/test4"
    )

    create_source_sql = (
        "insert into article_sources (name, url, description, created_at) "
        "values ('DW Germany Feed', 'https://rss.dw.com/rdf/rss-en-ger', 'DW feed about germany', now());"
    )

    article_service = ArticleService(session=session)
    await article_service.save_article_source(url="url.url.com/url1", name="feed1", description="feed description")
    await article_service.save_articles(entries=[test1, test2, test3, test4], feed_id=1)
