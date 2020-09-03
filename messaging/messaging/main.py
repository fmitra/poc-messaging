import asyncio

from aiohttp import web

from .routes import add_routes


def create_application(loop):
    app = web.Application(loop=loop)
    add_routes(app)
    return app


def main():
    loop = asyncio.get_event_loop()
    app = create_application(loop)
    web.run_app(app)
