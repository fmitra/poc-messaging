import logging
import asyncio

from aiohttp import web

from messaging import config
from messaging.routes import add_routes


def configure():
    if not config.APP_SECRET:
        raise ValueError('config.APP_SECRET is not configured')

    if not config.SOCKET_SECRET:
        raise ValueError('config.SOCKET_SECRET is not configured')

    if not config.DEBUG:
        return

    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    loop.set_debug(True)


def create_application() -> web.Application:
    configure()
    app = web.Application()
    add_routes(app)
    return app


def main():
    app = create_application()
    web.run_app(app)
