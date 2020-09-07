from functools import wraps
from typing import Callable, Dict, Awaitable, Any

import jwt
from aiohttp import web

from messaging import config


Handler = Callable[[web.Request], Awaitable[Any]]


def require_auth(view: Handler):
    @wraps(view)
    async def middleware(request: web.Request):
        decoded: Dict
        token = request.headers \
            .get('AUTHORIZATION', '') \
            .replace('Bearer ', '')

        try:
            decoded = jwt.decode(
                str.encode(token),
                config.SECRET,
                algorithm=[config.JWT_ALG],
            )
        except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError):  # type: ignore
            raise web.HTTPForbidden()

        if decoded != {}:
            raise web.HTTPForbidden()

        return await view(request)
    return middleware
