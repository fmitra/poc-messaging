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
    user_id: str
    content: str


message_schema = Schema({
    'user_id': str,
    'content': str,
})
