"""Websocket lifecycele management.

User websockets are stored in memory. Message delivery
is backed by a Redis PubSub which is used to monitor
incoming messages and publish the messages to the correct
socket.

"""
import logging
import json
from typing import Optional, List, Dict, Union
import asyncio

import redis
from aiohttp import web
from schema import SchemaError

from messaging.types import Message, message_schema


NOTIFICATION_CHANNEL = 'notifications'

logger = logging.getLogger(__name__)


class Sockets:
    """Sockets tracks and coordinates messages to user websockets."""
    def __init__(self, r: redis.Redis, channel_name: str = NOTIFICATION_CHANNEL):
        self.sockets: Dict[str, List[web.WebSocketResponse]] = {}
        self.redis = r
        self.channel = r.pubsub()
        self.channel.subscribe(channel_name)

    def set_socket(self, user_id: str, ws: web.WebSocketResponse):
        """Store a socket in memory, referenced by user_id."""
        with self.redis.lock(user_id):
            open_sockets = self.sockets.setdefault(user_id, [])
            open_sockets.append(ws)

    def get_sockets(self, user_id: str) -> List[web.WebSocketResponse]:
        """Retrieve all open sockets for a user_id."""
        return self.sockets.get(user_id, [])

    def monitor(self, loop: asyncio.BaseEventLoop):
        """Monitor for new messages published to the subscribed Redis channel.

        When a message is received, it will be published to all
        available websockets associated with a specific user ID.

        """
        # `listen()` blocks forever so we monitor for messages
        # in a separate event loop in a new thread running as a daemon.
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(self._handle_new_messages())

    async def close_socket(self, user_id: str, ws: web.WebSocketResponse):
        """Close a socket and remove it from in-memory storage."""
        with self.redis.lock(user_id):
            sockets = self.get_sockets(user_id)
            if ws in sockets:
                sockets.remove(ws)

            await ws.close()

    async def shut_down(self):
        """Close all open sockets."""
        futures = [
            socket.close() for user_sockets in self.sockets.values()
            for socket in user_sockets
        ]
        await asyncio.gather(*futures)

    async def process(self, message: Message):
        """Submit a message to all available sockets for a particular user."""
        user_id = message['user_id']
        sockets = self.get_sockets(user_id)
        if not sockets:
            return

        outgoing = [s.send_str(message['content']) for s in sockets]
        await asyncio.gather(*outgoing)

    async def publish(self, msg: Message) -> bool:
        """Publish a message to a Redis channel.

        Consumers subscribed to the channel check if open sockets
        exist for the designated user. If a socket is found, the
        message will be delivered to all available sockets.

        """
        try:
            message_schema.validate(msg)
        except SchemaError:
            return False

        b = json.dumps(msg)

        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(
            None, self.redis.publish, NOTIFICATION_CHANNEL, b,
        )
        await future

        return True

    async def _handle_new_messages(self):
        for msg in self.channel.listen():
            data = serialize(msg['data'])
            if data:
                await self.process(data)


def serialize(msg: Union[str, bytearray, bytes]) -> Optional[Message]:
    """Serialize a message to the expected Redis PubSub format."""
    try:
        data = json.loads(msg)
    except TypeError:
        # We receive an int from redis on initial connections
        # We can safely ignore this
        return None
    except json.decoder.JSONDecodeError:
        logger.exception('invalid JSON')
        return None

    try:
        message_schema.validate(data)
    except SchemaError:
        logger.exception('invalid message schema')
        return None

    return data
