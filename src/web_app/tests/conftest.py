import pytest
from sqlalchemy import create_engine
from sqlalchemy_utils import drop_database, create_database, database_exists
from starlette.testclient import TestClient

from db import session, metadata
from config import settings
from web_app.main import routes, middleware
from starlette.applications import Starlette
from sqlalchemy.ext.asyncio import AsyncSession


app = Starlette(routes=routes, middleware=middleware)


@pytest.fixture(scope="session", autouse=True)
def test_db_url():
    return settings.db_url.with_name("test-db")


@pytest.fixture(scope="session", autouse=True)
def sync_test_db_url(test_db_url):
    return test_db_url.with_scheme("postgresql+psycopg2")


@pytest.fixture(scope="session", autouse=True)
def db_engine(sync_test_db_url):
    url = str(sync_test_db_url)
    engine = create_engine(url)
    exist = database_exists(url)
    if exist:
        drop_database(url)
    create_database(url)
    metadata.create_all(engine)  # Create the tables.
    yield engine  # Run the tests.
    drop_database(url)

@pytest.fixture(scope="session", autouse=True)
@pytest.mark.asyncio
def test_engine(test_db_url):
    return session.make_engine(db_url=str(test_db_url))

@pytest.fixture
def test_client(test_engine):
    app.state.db_engine = test_engine
    return TestClient(app)
