from unittest import mock

import jwt
import pytest
from aiohttp import web

from messaging.views import healthcheck
from messaging.authentication import (
    create_token,
    is_token_valid,
    get_username,
    get_socket_token,
    get_app_token,
    require_auth,
)
from messaging import config


def test_creates_token():
    token = create_token(config.APP_SECRET, 'test-user')
    assert is_token_valid(token, config.APP_SECRET) is True
    assert is_token_valid(token, 'bad-secret') is False


def test_gets_username():
    token = create_token(config.APP_SECRET, 'username')
    username = get_username(token)
    assert username == 'username'


def test_retrieves_token_from_query_params():
    request = mock.Mock(spec=web.Request)
    request.headers = {
        'AUTHORIZATION': 'Bearer Token',
    }
    assert get_app_token(request) == 'Token'


def test_retrieves_token_from_headers():
    request = mock.Mock(spec=web.Request)
    request.rel_url.query = {
        'authorization': 'Token'
    }
    assert get_socket_token(request) == 'Token'


async def test_requires_authentication():
    request = {'token': ''}
    with pytest.raises(web.HTTPForbidden):
        await require_auth(healthcheck)(request)
