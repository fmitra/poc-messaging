from aiohttp import web

from messaging.views import (
    healthcheck,
    token,
    socket,
    socket_token,
    message,
)


def add_routes(app: web.Application):
    app.router.add_routes([
        web.get('/healthcheck', healthcheck, name='healthcheck'),
        web.get('/token', token, name='token'),
        web.get('/ws/token', socket_token, name='socket_token'),
        web.get('/ws', socket, name='socket'),
        web.post('/message', message, name='message'),
    ])
