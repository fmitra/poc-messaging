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

    for i in range(10):
        await active_sockets.publish({
            'user_id': 'fe63a8f7e6c643a3aca98f639e5604d1',
            'content': 'hello world',
        })

    assert process_mock.call_count == 10
