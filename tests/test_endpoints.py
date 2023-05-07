"""Tests for endpoints."""

import pytest

from shortify.models import UrlMap, User

py_url = "https://www.python.org"

API_CREATE_URL = "/api/id/"


def test_create_id(client):
    
    got = client.post(
        API_CREATE_URL,
        json={
            "original_link"
            
        },
    )
    assert (
        got.status_code == 201
    ), "When creating a short link in the answer, the status code should be 201."
    assert list(got.json.keys()) == [
        "short_link",
        "url",
    ], "When creating a short link, the response should contain the `short_link` and `url` keys."
    assert got.json == {
        "url": py_url,
        "short_link": "http://localhost/py",
    }, "The response when creating a short link does not match the specification."


def test_create_empty_body(client):
    try:
        got = client.post(API_CREATE_URL)
    except Exception as e:
        raise AssertionError(
            "When creating a short link without a body in the request, "
            'an exception should be raised with the message "Missing JSON in request".'
        ) from e
    assert (
        got.status_code == 400
    ), "When creating a short link without a body in the request, the status code should be 400."
    assert list(got.json.keys()) == [
        "message"
    ], "When creating a short link without a body in the request, the response should contain the `message` key."
    assert got.json == {"message": "Request body is missing"}, (
        "When creating a short link without a body in the request, "
        "the response does not match the specification."
    )


@pytest.mark.parametrize(
    "json_data",
    [
        ({"url": py_url, "custom_id": ".,/!?"}),
        ({"url": py_url, "custom_id": "Hodor-Hodor"}),
        ({"url": py_url, "custom_id": "h@k$r"}),
        ({"url": py_url, "custom_id": "$"}),
        ({"url": py_url, "custom_id": "п"}),
        ({"url": py_url, "custom_id": "l l"}),
    ],
)
def test_invalid_short_url(json_data, client):
    got = client.post(API_CREATE_URL, json=json_data)
    assert (
        got.status_code == 400
    ), "If the name for the short link is invalid, the response should have status 400."
    assert list(got.json.keys()) == [
        "message"
    ], "If the name for the short link is invalid, the response should contain the `message` key."
    assert got.json == {"message": "Invalid short link name specified"}, (
        "If the name for the short link is invalid, the response does not match the specification."
        "The message should be `An invalid name was specified for a short link`."
    )
    unique_id = UrlMap.query.filter_by(original=py_url).first()
    assert not unique_id, (
        "If the name for the short link is invalid, "
        "the short link should not be created in the database."
    )


def test_no_required_field(client):
    try:
        got = client.post(
            API_CREATE_URL,
            json={
                "short_link": "python",
            },
        )
    except Exception as e:
        raise AssertionError(
            "If the body of the request to the `/api/id/` endpoint is different than expected - "
            "raise an exception with the message `Missing JSON in request`.",
        ) from e
    assert got.status_code == 400, (
        "If the body of the request to the `/api/id/` endpoint is different than expected -"
        "return status code 400."
    )
    assert list(got.json.keys()) == ["message"], (
        "If the body of the request to the `/api/id/` endpoint is different than expected - "
        "return a response with the `message` key."
    )
    assert got.json == {"message": '"url" is a required field!'}, (
        "If the body of the request to the `/api/id/` endpoint is different than expected - "
        'return a response with the message `"url" is a required field!`.'
    )


def test_url_already_exists(client, short_python_url):
    try:
        got = client.post(
            API_CREATE_URL,
            json={
                "url": py_url,
                "custom_id": "py",
            },
        )
    except Exception as e:
        raise AssertionError(
            "When trying to create a link with a short name that is already taken - ",
            "raise an exception with the message ``The name py is already taken!``.",
        ) from e
    assert got.status_code == 400, (
        "When trying to create a link with a short name that is already taken -"
        "return status code 400."
    )
    assert list(got.json.keys()) == ["message"], (
        "When trying to create a link with a short name that is already taken - "
        "return a response with the `message` key."
    )
    assert got.json == {"message": "The name py is already taken!"}, (
        "When trying to create a link with a short name that is already taken - "
        "return a response with the message `The name py is already taken!`."
    )


@pytest.mark.parametrize(
    "json_data",
    [
        ({"url": py_url, "custom_id": None}),
        ({"url": py_url, "custom_id": ""}),
    ],
)
def test_generated_unique_short_id(json_data, client):
    try:
        got = client.post(API_CREATE_URL, json=json_data)
    except Exception as e:
        raise AssertionError(
            "For a request where short_id is missing or contains an empty string - "
            "generate a unique short_id and return it in the response."
        ) from e
    assert got.status_code == 201, (
        "For a request where short_id is missing or contains an empty string - "
        "generate a unique short_id and return it in the response."
    )
    unique_id = UrlMap.query.filter_by(original=py_url).first()
    assert unique_id, (
        "When creating a short link without an explicit name "
        "you need to generate a relative part of the link"
        "from digits and lowercase latin characters - and return the link in the API response."
    )
    assert got.json == {
        "url": py_url,
        "short_link": "http://localhost/" + unique_id.short,
    }, (
        "When creating a short link without an explicit name "
        "you need to generate a relative part of the link"
        "from digits and lowercase latin characters - and return the link in the API response."
    )


def test_get_url_endpoint(client, short_python_url):
    got = client.get(f"/api/id/{short_python_url.short}/")
    assert (
        got.status_code == 200
    ), "In response to a GET request to the `/api/id/<short_id>/` endpoint, status code 200 should be returned"
    assert list(got.json.keys()) == [
        "url"
    ], "In response to a GET request to the `/api/id/<short_id>/` endpoint, the `url` key should be returned"
    assert got.json == {"url": py_url}, (
        "In response to a GET request to the `/api/id/<short_id>/` endpoint, "
        "the value of the `url` key should be the original URL."
    )


def test_get_url_not_fount(client):
    got = client.get("/api/id/{enexpected}/")
    assert got.status_code == 404, (
        "In response to a GET request to the `/api/id/<short_id>/` endpoint, "
        "if the short link does not exist, status code 404 should be returned."
    )
    assert list(got.json.keys()) == ["message"], (
        "In response to a GET request to the `/api/id/<short_id>/` endpoint, "
        "if the short link does not exist, the `message` key should be returned."
    )
    assert got.json == {"message": "Specified id was not found"}, (
        "In response to a GET request to the `/api/id/<short_id>/` endpoint, "
        "if the short link does not exist, the message `The specified id was not found` should be returned."
    )


def test_len_short_id_api(client):
    long_string = "CuriosityisnotasinHarryHoweverfromtimetotimeyoushouldexercisecaution"
    got = client.post(
        API_CREATE_URL,
        json={
            "url": py_url,
            "custom_id": long_string,
        },
    )
    assert got.status_code == 400, (
        "If the POST request to the `/api/id/` endpoint contains a field `short_id` "
        "with a string longer than 16 characters - return status code 400."
    )
    assert list(got.json.keys()) == ["message"], (
        "If the POST request to the `/api/id/` endpoint contains a field `short_id` "
        "with a string longer than 16 characters - return a response with the `message` key."
        "The value of the `message` key should be "
    )
    assert got.json == {"message": "Invalid short link name specified"}, (
        "If the POST request to the `/api/id/` endpoint contains a field `short_id` "
        "with a string longer than 16 characters - return a response with the `message` key."
        "The value of the `message` key should be "
    )


def test_len_short_id_autogenerated_api(client):
    client.post(
        API_CREATE_URL,
        json={
            "url": py_url,
        },
    )
    unique_id = UrlMap.query.filter_by(original=py_url).first()
    assert len(unique_id.short) == 6, (
        "If the POST request to the `/api/id/` endpoint does not contain a field `short_id` - "
        "generate a unique short_id and return it in the response."
    )
