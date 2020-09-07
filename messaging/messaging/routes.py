from aiohttp import web

from messaging.views import (
    healthcheck,
    token,
    connect,
)


def add_routes(app: web.Application):
    app.router.add_routes([
        web.get('/healthcheck', healthcheck, name='healthcheck'),
        web.get('/token', token, name='token'),
        web.get('/connect', connect, name='connect'),
    ])
