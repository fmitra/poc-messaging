import logging

from aiohttp import (
    WSMsgType,
    web,
)

from messaging import config
from messaging.sockets import active_sockets
from messaging.authentication import (
    require_auth,
    require_socket_auth,
    create_token,
    get_user_id,
    get_app_token,
    get_socket_token,
    AppSecret,
    SocketSecret,
)


logger = logging.getLogger(__name__)


async def healthcheck(request: web.Request) -> web.Response:
    return web.Response(text='ok')


async def token(request: web.Request) -> web.Response:
    token = create_token(AppSecret)
    return web.json_response({
        'token': token,
    })


@require_auth
async def socket_token(request: web.Request) -> web.Response:
    user_id = get_user_id(get_app_token(request))
    token = create_token(SocketSecret, user_id)
    return web.json_response({
        'token': token,
    })


@require_socket_auth
async def socket(request: web.Request) -> web.WebSocketResponse:
    token = get_socket_token(request)
    user_id = get_user_id(token)

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    active_sockets.set_socket(user_id, ws)

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            if msg.data == 'close':
                await active_sockets.close_socket(user_id, ws)
            else:
                await ws.send_str(msg.data + ' /answer')
        elif msg.type == WSMsgType.ERROR:
            logger.info('ws connection closed with exception %s' % ws.exception())
    return ws
