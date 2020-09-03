from aiohttp import web

from .views import (
    healthcheck,
)

def add_routes(app):
    app.router.add_routes([
        web.get('/healthcheck', healthcheck, name='healthcheck'),
    ])
