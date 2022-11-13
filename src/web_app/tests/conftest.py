import asyncio

import pytest
import sqlalchemy
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import drop_database, create_database, database_exists
from starlette.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from starlette.applications import Starlette
from unittest import mock

from db import metadata
from config import settings
from web_app.main import routes, middleware

db_url = settings.db_url.with_name("test-db")
async_engine = create_async_engine(str(db_url), pool_size=10, echo=True, max_overflow=10)


TestingAsyncSessionLocal = sessionmaker(
    async_engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
    class_=AsyncSession,
)

app = Starlette(routes=routes, middleware=middleware)
app.state.db_engine = async_engine


@pytest.fixture(scope="session")
def event_loop():
    """
    Creates an instance of the default event loop for the test session.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def client() -> TestClient:
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
def db_engine():
    url = str(db_url.with_scheme("postgresql+psycopg2"))
    engine = create_engine(url)
    exist = database_exists(url)
    if exist:
        drop_database(url)
    create_database(url)
    metadata.create_all(engine)  # Create the tables.
    yield engine  # Run the tests.
    drop_database(url)


@pytest_asyncio.fixture(scope="function")
async def async_db_session():
    """The expectation with async_sessions is that the
    transactions be called on the connection object instead of the
    session object.
    Detailed explanation of async transactional tests
    <https://github.com/sqlalchemy/sqlalchemy/issues/5811>
    """

    connection = await async_engine.connect()
    trans = await connection.begin()
    async_session = TestingAsyncSessionLocal(bind=connection)
    nested = await connection.begin_nested()

    @sqlalchemy.event.listens_for(async_session.sync_session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested

        if not nested.is_active:
            nested = connection.sync_connection.begin_nested()

    yield async_session

    await trans.rollback()
    await async_session.close()
    await connection.close()
