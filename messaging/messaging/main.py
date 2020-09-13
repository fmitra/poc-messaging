"""Main application package

Responsible for configuring application and
dependencies for HTTP server.

"""
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
    """Configure application settings."""
    if not config.APP_SECRET:
        raise ValueError('config.APP_SECRET is not configured')

    if not config.SOCKET_SECRET:
        raise ValueError('config.SOCKET_SECRET is not configured')

    if not config.DEBUG:
        return

    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    loop.set_debug(True)


def add_dependencies(app: web.Application):
    """Inject dependencies."""
    sockets = Sockets(redis.Redis(**config.REDIS))
    app['sockets'] = sockets


async def close_sockets(app: web.Application):
    """Application cleanup on shutdown."""
    sockets = app['sockets']
    await sockets.shut_down()


async def monitor_messages(app: web.Application):
    """Background task to monitor for incoming messages.

    redis-py library is not async and will block when
    listening to incoming messages, so we run it in a separate
    thread.

    """
    sockets = app['sockets']
    loop = asyncio.new_event_loop()
    thread = threading.Thread(target=sockets.monitor, args=(loop,), daemon=True)
    thread.start()


def create_application() -> web.Application:
    """Start up the application."""
    configure()

    app = web.Application(middlewares=(
        user_middleware(),
    ))
    add_dependencies(app)
    add_routes(app)

    app.on_cleanup.append(close_sockets)
    app.on_startup.append(monitor_messages)

    return app


def main():
    """Run web server."""
    app = create_application()
    web.run_app(app)
