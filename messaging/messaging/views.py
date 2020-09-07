import jwt
from aiohttp import web

from messaging import config
from messaging.authentication import require_auth


async def healthcheck(request: web.Request) -> web.Response:
    return web.Response(text='ok')


async def token(request: web.Request) -> web.Response:
    token = jwt.encode({}, config.SECRET, algorithm=config.JWT_ALG)
    return web.json_response({
        'token': token.decode(),
    })


@require_auth
async def connect(request: web.Request) -> web.Response:
    return web.Response(text='ok')
