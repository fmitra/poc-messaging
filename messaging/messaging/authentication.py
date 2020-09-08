from uuid import uuid4
from datetime import datetime, timedelta
from functools import wraps
from typing import (
    NewType,
    Callable,
    Dict,
    Awaitable,
    Any,
    Optional,
)

import jwt
from aiohttp import web

from messaging import config


Secret = NewType('Secret', str)
AppSecret = Secret(config.APP_SECRET)
SocketSecret = Secret(config.SOCKET_SECRET)

Handler = Callable[[web.Request], Awaitable[Any]]


def require_socket_auth(view: Handler):
    @wraps(view)
    async def middleware(request: web.Request):
        token = get_socket_token(request)
        if not is_token_valid(token, SocketSecret):
            raise web.HTTPForbidden()

        return await view(request)
    return middleware


def require_auth(view: Handler):
    @wraps(view)
    async def middleware(request: web.Request):
        token = get_app_token(request)
        if not is_token_valid(token, AppSecret):
            raise web.HTTPForbidden()

        return await view(request)
    return middleware


def is_token_valid(token: str, secret: Secret, user_id: Optional[str] = None) -> bool:
    decoded: Dict = {}

    try:
        decoded = jwt.decode(
            str.encode(token),
            secret,
            algorithm=[config.JWT_ALG],
        )
    except jwt.exceptions.PyJWTError:  # type: ignore
        return False

    if user_id and user_id != decoded.get('user_id', ''):
        return False

    return True


def create_token(secret: Secret, user_id: Optional[str] = None) -> str:
    minutes_till_expiry = 30 if Secret == AppSecret else 1
    exp = datetime.now() + timedelta(minutes=minutes_till_expiry)

    token = jwt.encode(
        {
            'exp': int(exp.strftime('%s')),
            'user_id': user_id or uuid4().hex,
        },
        secret,
        algorithm=config.JWT_ALG,
    )

    return token.decode()


def get_user_id(token: str) -> str:
    try:
        decoded = jwt.decode(str.encode(token), verify=False)
    except jwt.exceptions.PyJWTError:  # type: ignore
        decoded = {}

    return decoded.get('user_id', '')


def get_app_token(request: web.Request) -> str:
    token = request.headers \
        .get('AUTHORIZATION', '') \
        .replace('Bearer ', '')

    return token


def get_socket_token(request: web.Request) -> str:
    params = request.rel_url.query
    return params.get('token', '')
