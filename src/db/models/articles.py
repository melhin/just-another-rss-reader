import sqlalchemy

from src.db import metadata

# metadata = sqlalchemy.MetaData()

articles = sqlalchemy.Table(
    "articles",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("hash", sqlalchemy.TEXT, nullable=False, unique=True),
    sqlalchemy.Column("title", sqlalchemy.TEXT, nullable=False),
    sqlalchemy.Column("url", sqlalchemy.TEXT, nullable=False, unique=True),
    sqlalchemy.Column("url2", sqlalchemy.TEXT, nullable=False, unique=True),
    sqlalchemy.Column("description", sqlalchemy.TEXT, nullable=True),
    sqlalchemy.Column("feed_url", sqlalchemy.TEXT, nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False),
)

article_keywords = sqlalchemy.Table(
    "article_keywords",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("keyword", sqlalchemy.TEXT, nullable=False, unique=True),
    sqlalchemy.Column("article_id", sqlalchemy.ForeignKey("articles.id"), nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False),
)
