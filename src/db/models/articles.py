from enum import Enum

import sqlalchemy
import sqlalchemy.dialects.postgresql as pg

from db import metadata


class CategoryEnum(Enum):
    GENERAL = "general"
    WORLD = "world"
    KERALA = "kerala"
    INDIA = "india"
    TECH = "tech"
    GERMANY = "germany"


article_sources = sqlalchemy.Table(
    "article_sources",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.TEXT, nullable=False),
    sqlalchemy.Column("url", sqlalchemy.TEXT, nullable=False, unique=True),
    sqlalchemy.Column("description", sqlalchemy.TEXT, nullable=True),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column("priority", sqlalchemy.Integer, default=0),
    sqlalchemy.Column("active", sqlalchemy.BOOLEAN, server_default=sqlalchemy.true()),
    sqlalchemy.Column("categories", pg.ARRAY(sqlalchemy.String), server_default="{}"),
)

articles = sqlalchemy.Table(
    "articles",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("hash", sqlalchemy.TEXT, nullable=False, unique=True),
    sqlalchemy.Column("title", sqlalchemy.TEXT, nullable=False),
    sqlalchemy.Column("url", sqlalchemy.TEXT, nullable=False, unique=True),
    sqlalchemy.Column("description", sqlalchemy.TEXT, nullable=True),
    sqlalchemy.Column("article_source_id", sqlalchemy.ForeignKey("article_sources.id")),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False),
)

article_keywords = sqlalchemy.Table(
    "article_keywords",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("keyword", sqlalchemy.TEXT, nullable=False),
    sqlalchemy.Column("article_id", sqlalchemy.ForeignKey("articles.id"), nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False),
)
