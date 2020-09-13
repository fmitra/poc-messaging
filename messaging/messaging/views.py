"""Application views"""
import json
import asyncio
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


async def healthcheck(_: web.Request) -> web.Response:
    """Application health check. Returns status `200`, result 'ok'."""
    return web.Response(text='ok')


async def app_token(_: web.Request) -> web.Response:
    """Generate an authorization token."""
    token = create_token(config.APP_SECRET)
    return web.json_response({
        'token': token,
    })


async def message(request: web.Request) -> web.Response:
    """Send a message to a specific user.

    Messages will be sent to all available websockets
    for the user.

    """
    try:
        msg = await request.json()
    except (json.decoder.JSONDecodeError, TypeError) as exc:
        raise web.HTTPBadRequest from exc

    try:
        message_schema.validate(msg)
    except SchemaError as exc:
        raise web.HTTPBadRequest from exc

    sockets = request.app['sockets']
    asyncio.ensure_future(sockets.publish(msg))
    return web.json_response({
        'status': 'ok',
    })


@require_auth
async def socket_token(request: web.Request) -> web.Response:
    """Create a short lived websocket authorization token.

    Websocket authorization tokens may be passed as a URL
    query param and have a 1 minute expiry. A user must be
    previously authenticated to generate the token.

    """
    token = create_token(config.SOCKET_SECRET, request['user_id'])
    return web.json_response({
        'token': token,
    })


@require_auth
async def socket(request: web.Request) -> web.WebSocketResponse:
    """Create a websocket connection.

    On success, a refernce to the token is stored in-memory
    with the user ID.

    """
    user_id = request['user_id']
    sockets = request.app['sockets']

    ws = web.WebSocketResponse(autoping=True, heartbeat=10)
    await ws.prepare(request)

    await sockets.set_socket(user_id, ws)

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                await ws.send_str(msg.data)
            if msg.type in (WSMsgType.CLOSED, WSMsgType.CLOSE):
                await sockets.close_socket(user_id, ws)
            if msg.type == WSMsgType.ERROR:
                await sockets.close_socket(user_id, ws)
                logger.error(
                    'ws connection closed with exception %s', ws.exception(),
                )
    finally:
        await sockets.close_socket(user_id, ws)

    return ws
