from uuid import uuid4
from datetime import datetime, timedelta
from functools import wraps
from typing import (
    Dict,
    Awaitable,
    Optional,
)

import jwt
from aiohttp import web

from messaging import config
from messaging.types import HTTPHandler


def require_auth(view: HTTPHandler):
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
    decoded: Dict = {}

    try:
        decoded = jwt.decode(
            str.encode(token),
            secret,
            algorithm=[config.JWT_ALG],
        )
    except jwt.exceptions.PyJWTError:  # type: ignore
        return False

    return True


def create_token(secret: str, user_id: Optional[str] = None) -> str:
    minutes_till_expiry = 30 if secret == config.APP_SECRET else 1
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
