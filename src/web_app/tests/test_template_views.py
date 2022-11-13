from unittest import mock


@mock.patch("web_app.main.get_articles_for_request")
def test_home_blank(mock_db_session, client):
    mock_db_session.return_value = [], 0
    response = client.get("/")
    assert response.status_code == 200
    assert "Total Articles: 0" in response.text


@mock.patch("web_app.main.get_articles_for_request")
def test_home_with_results(mock_db_session, client):
    mocked_response = [
        {"description": "test2 description", "feed": "feed2", "title": "test2", "url": "https://test.com/test2"},
        {"description": "test1 description", "feed": "feed1", "title": "test1", "url": "https://test.com/test1"},
    ]
    mock_db_session.return_value = mocked_response, 2
    response = client.get("/")
    assert response.status_code == 200
    assert "Total Articles: 2" in response.text
    values = [value for resp in mocked_response for value in resp.values()]
    for value in values:
        assert value in response.text
    assert "Next" not in response.text
    assert "Previous" not in response.text


@mock.patch("web_app.main.get_articles_for_request")
def test_home_with_paginated_results(mock_db_session, client):
    mocked_response = [
        {"description": "test2 description", "feed": "feed2", "title": "test2", "url": "https://test.com/test2"},
        {"description": "test1 description", "feed": "feed1", "title": "test1", "url": "https://test.com/test1"},
    ]
    mock_db_session.return_value = mocked_response, 10
    response = client.get("/?offset=0&limit=2")
    assert response.status_code == 200
    assert "Total Articles: 10" in response.text
    values = [value for resp in mocked_response for value in resp.values()]
    for value in values:
        assert value in response.text
    assert "Next" in response.text
    assert "Previous" not in response.text

    # checking for previous when we have moved to a different offset
    response = client.get("/?offset=4&limit=2")
    assert "Next" in response.text
    assert "Previous" in response.text
