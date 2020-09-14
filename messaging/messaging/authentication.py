"""Authentication management

Provides token generation, validation and other
auth/identity related functions.

"""
from datetime import datetime, timedelta
from functools import wraps

import jwt
from aiohttp import web

from messaging import config
from messaging.types import HTTPHandler


def require_auth(view: HTTPHandler):
    """Enforces authentication requirements on a view.

    A token may be passed either in a header or as a URL
    query parameter (in the case of a websocket).

    """
    @wraps(view)
    async def middleware(request: web.Request):
        token = request['token']

        is_valid = (
            is_token_valid(token, config.APP_SECRET) or
            is_token_valid(token, config.SOCKET_SECRET)
        )
        if not is_valid:
            raise web.HTTPForbidden()

        return await view(request)
    return middleware


def is_token_valid(token: str, secret: str) -> bool:
    """Validates a token with a given secret."""
    try:
        jwt.decode(
            str.encode(token),
            secret,
            algorithms=[config.JWT_ALG],
        )
    except jwt.exceptions.PyJWTError:  # type: ignore
        return False

    return True


def create_token(secret: str, username: str) -> str:
    """Creates a new JWT token with a given secret.

    If a user ID is not provided, it will be created automatically.
    By default tokens have a 30 minute expiry. Socket tokens,
    however have a 1 minute validity as they are expected to be
    passed as a URL query parameter which is less secure.

    """
    minutes_till_expiry = 30 if secret == config.APP_SECRET else 1
    exp = datetime.now() + timedelta(minutes=minutes_till_expiry)

    token = jwt.encode(
        {
            'exp': int(exp.strftime('%s')),
            'username': username,
        },
        secret,
        algorithm=config.JWT_ALG,
    )

    return token.decode()


def get_username(token: str) -> str:
    """Retrieves a username from a JWT token."""
    try:
        decoded = jwt.decode(
            str.encode(token),
            verify=False,
            algorithms=[config.JWT_ALG],
        )
    except jwt.exceptions.PyJWTError:  # type: ignore
        decoded = {}

    return decoded.get('username', '')


def get_app_token(request: web.Request) -> str:
    """Retrieves JWT token from a request header."""
    token = request.headers \
        .get('AUTHORIZATION', '') \
        .replace('Bearer ', '')
    return token


def get_socket_token(request: web.Request) -> str:
    """Retrieves JWT token from a query parameter."""
    params = request.rel_url.query
    return params.get('authorization', '')
