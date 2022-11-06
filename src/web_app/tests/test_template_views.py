import pytest
from unittest import mock
from web_app.tests.factories import create_articles
from db.session import get_test_session


def test_home_blank(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert "Total Articles: 0" in response.text


@pytest.mark.asyncio
async def test_home_with_results(test_client, test_engine):
    async with get_test_session(db_engine=test_engine) as session:
        print("Creating articles")
        await create_articles(session=session)

    response = test_client.get("/")
    print("Calling articles")
    assert response.status_code == 200
    assert "Total Articles: 4" in response.text


@pytest.mark.asyncio
async def test_home_with_paginated_results(test_client, initial_data):
    response = test_client.get("/")
    assert response.status_code == 200
    assert "Total Articles: 2" in response.text
