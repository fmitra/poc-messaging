"""Application types"""
from typing import (
    Awaitable,
    Any,
    Callable,
    TypedDict,
)

from aiohttp import web
from schema import Schema


HTTPHandler = Callable[[web.Request], Awaitable[Any]]


class Message(TypedDict):
    """Represents a message for Redis PubSub."""
    username: str
    content: str


token_schema = Schema({
    'username': str,
})


message_schema = Schema({
    'username': str,
    'content': str,
})
