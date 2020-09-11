import logging
import asyncio
import threading

from aiohttp import web
import redis

from messaging import config
from messaging.middleware import user_middleware
from messaging.routes import add_routes
from messaging.sockets import Sockets


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


def dependencies(app: web.Application):
    sockets = Sockets(redis.Redis(**config.REDIS))
    app['sockets'] = sockets


def create_application() -> web.Application:
    configure()
    app = web.Application(middlewares=(
        user_middleware(),
    ))
    dependencies(app)
    add_routes(app)
    return app


def main():
    app = create_application()
    sockets = app['sockets']
    loop = asyncio.new_event_loop()
    thread = threading.Thread(target=sockets.monitor, args=(loop,), daemon=True)

    thread.start()
    web.run_app(app)
