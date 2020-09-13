"""Application routes"""
from aiohttp import web

from messaging.views import (
    healthcheck,
    app_token,
    socket_token,
    socket,
    message,
)


def add_routes(app: web.Application):
    """Configure routing for the application."""
    app.router.add_routes([
        web.get('/healthcheck', healthcheck, name='healthcheck'),
        web.get('/token', app_token, name='app_token'),
        web.get('/ws/token', socket_token, name='socket_token'),
        web.get('/ws', socket, name='socket'),
        web.post('/message', message, name='message'),
    ])
