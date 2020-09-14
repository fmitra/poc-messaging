"""Middleware

Middleware is applied universally to all app views.

"""
from aiohttp import web

from messaging.types import HTTPHandler
from messaging.authentication import (
    get_username,
    get_app_token,
    get_socket_token,
)


def user_middleware():
    """Configure the request object with the user's identity.

    Tokens may be provided through request headers or a URL query
    params. We default to the request header if available.
    Tokens are unpacked and the user ID is additionally
    set to the request.

    """
    @web.middleware
    async def middleware(request: web.Request, handler: HTTPHandler):
        token = get_app_token(request) or get_socket_token(request)
        username = get_username(token)
        request['username'] = username
        request['token'] = token
        return await handler(request)
    return middleware
