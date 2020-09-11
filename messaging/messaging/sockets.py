import concurrent
import logging
import json
from typing import Optional, List, Dict, Any, Union
import asyncio

import redis
from aiohttp import web
from schema import SchemaError

from messaging import config
from messaging.types import Message, message_schema


NOTIFICATION_CHANNEL = 'notifications'

logger = logging.getLogger(__name__)


class Sockets:
    def __init__(self, r: redis.Redis, channel_name: str = NOTIFICATION_CHANNEL):
        self.sockets: Dict[str, List[web.WebSocketResponse]] = {}
        self.redis = r
        self.channel = r.pubsub()
        self.channel.subscribe(channel_name)

    def set_socket(self, user_id: str, ws: web.WebSocketResponse):
        with self.redis.lock(user_id):
            open_sockets = self.sockets.setdefault(user_id, [])
            open_sockets.append(ws)

    def get_sockets(self, user_id: str) -> List[web.WebSocketResponse]:
        return self.sockets.get(user_id, [])

    def monitor(self, loop: asyncio.BaseEventLoop):
        # `listen()` blocks forever so we monitor for messages
        # in a separate event loop in a new thread running as a daemon.
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(self._handle_new_messages())

    def serialize(self, msg: Union[bytes, int]) -> Optional[Message]:
        try:
            data = json.loads(msg)
        except TypeError:
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

    async def close_socket(self, user_id: str, ws: web.WebSocketResponse):
        with self.redis.lock(user_id):
            sockets = self.get_sockets(user_id)
            if ws in sockets:
                sockets.remove(ws)

            await ws.close()

    async def process(self, message: Message):
        user_id = message['user_id']
        sockets = self.get_sockets(user_id)
        if not sockets:
            return

        futures = [s.send_str(data['content']) for s in sockets]
        await asyncio.gather(*futures)

    async def publish_all(self, msg: Message):
        all_ws = self.get_sockets(msg['user_id'])
        if not all_ws:
            return

        outgoing = [ws.send_str(msg['content']) for ws in all_ws]
        await asyncio.gather(*outgoing)

    async def publish(self, msg: Message) -> bool:
        try:
            message_schema.validate(msg)
        except SchemaError:
            return False

        b = json.dumps(msg)

        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, self.redis.publish, NOTIFICATION_CHANNEL, b)
        await future

        return True

    async def _handle_new_messages(self):
        for msg in self.channel.listen():
            data = self.serialize(msg['data'])
            if data:
                await self.process(data)
