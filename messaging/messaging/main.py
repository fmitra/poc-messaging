import asyncio

from aiohttp import web

from messaging import config
from messaging.routes import add_routes


def configure():
    if not config.SECRET:
        raise ValueError('config.SECRET should be configured to a random string')

    if not config.DEBUG:
        return

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
