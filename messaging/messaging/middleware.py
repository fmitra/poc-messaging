from aiohttp import web

from messaging.types import HTTPHandler
from messaging.authentication import (
    get_user_id,
    get_app_token,
    get_socket_token,
)


def user_middleware():
    @web.middleware
    async def middleware(request: web.Request, handler: HTTPHandler):
        token = get_app_token(request) or get_socket_token(request)
        user_id = get_user_id(token)
        request['user_id'] = user_id
        request['token'] = token
        return await handler(request)
    return middleware
