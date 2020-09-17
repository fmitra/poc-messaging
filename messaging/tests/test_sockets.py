from unittest import mock
import json
import threading
import asyncio
import redis

from messaging.sockets import Sockets
from messaging import config


@mock.patch.object(Sockets, 'process')
async def test_processes_published_messages(process_mock):
    active_sockets = Sockets(redis.Redis(**config.REDIS))
    loop = asyncio.new_event_loop()
    t = threading.Thread(target=active_sockets.monitor, args=(loop,), daemon=True)
    t.start()

    futures = [
        active_sockets.publish({
            'username': 'test-user',
            'content': 'hello world',
        }) for _ in range(10)
    ]
    await asyncio.gather(*futures)
    assert process_mock.call_count == 10
