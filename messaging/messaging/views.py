import aiohttp
import logging

from aiohttp import (
    WSMsgType,
    web,
)
from schema import SchemaError

from messaging import config
from messaging.authentication import (
    create_token,
    require_auth,
)
from messaging.types import message_schema


logger = logging.getLogger(__name__)


async def healthcheck(request: web.Request) -> web.Response:
    return web.Response(text='ok')


async def token(request: web.Request) -> web.Response:
    token = create_token(config.APP_SECRET)
    return web.json_response({
        'token': token,
    })


async def message(request: web.Request) -> web.Response:
    try:
        msg = await request.json()
    except (json.decoder.JSONDecodeError, TypeError):
        raise web.HTTPBadRequest

    try:
        message_schema.validate(msg)
    except SchemaError:
        raise web.HTTPBadRequest

    sockets = request.app['sockets']
    aiohttp.ensure_future(sockets.publish_all(msg))
    return web.json_response({
        'status': 'ok',
    })


@require_auth
async def socket_token(request: web.Request) -> web.Response:
    token = create_token(config.SOCKET_SECRET, request['user_id'])
    return web.json_response({
        'token': token,
    })


@require_auth
async def socket(request: web.Request) -> web.WebSocketResponse:
    user_id = request['user_id']
    sockets = request.app['sockets']

    ws = web.WebSocketResponse(autoping=True, heartbeat=10)
    await ws.prepare(request)

    sockets.set_socket(user_id, ws)

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                await ws.send_str(msg.data)
            if msg.type in (WSMsgType.CLOSED, WSMsgType.CLOSE):
                await sockets.close_socket(user_id, ws)
            if msg.type == WSMsgType.ERROR:
                await sockets.close_socket(user_id, ws)
                logger.info('ws connection closed with exception %s' % ws.exception())
    finally:
        await sockets.close_socket(user_id, ws)

    return ws
