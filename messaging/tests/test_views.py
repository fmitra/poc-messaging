import asyncio
import jwt
import redis
from aiohttp.client_exceptions import WSServerHandshakeError

from messaging import config
from messaging.authentication import (
    get_username,
    is_token_valid,
)

from tests.helpers import (
    app_token,
    socket_token,
    ws_connect,
)


async def test_establishes_and_closes_multiple_ws_connections(client):
    sockets = client.app['sockets']
    token = await socket_token(client)

    username = get_username(token)
    ws1 = await ws_connect(client, token)
    ws2 = await ws_connect(client, token)

    await ws1.close()
    await ws1.receive()
    await asyncio.sleep(.1)
    assert len(sockets.get_sockets(username)) == 1


async def test_sends_message(client):
    token = await socket_token(client)
    username = get_username(token)
    ws = await ws_connect(client, token)

    resp = await client.post('/message', json={
        'username': username,
        'content': 'hello',
    })
    data = await resp.json()
    assert data['status'] == 'ok'

    msg = await ws.receive()
    assert msg.data == 'hello'


async def test_establishes_ws_connection(client):
    token = await socket_token(client)
    ws = await ws_connect(client, token)
    await ws.ping()

    await ws.send_str('hello world')
    msg = await ws.receive()
    assert msg.data == 'hello world'


async def test_fails_to_establish_ws_connection(client):
    try:
        ws = await ws_connect(client, 'invalid-token')
    except WSServerHandshakeError as e:
        assert e.status == 403
    else:
        raise Exception('Handshake should not succeed')


async def test_retrieves_socket_token(client):
    token = await app_token(client)
    resp = await client.post('/ws/token', headers={
        'Authorization': token,
    })
    data = await resp.json()
    assert 'token' in data
    assert is_token_valid(data['token'], config.SOCKET_SECRET) == True
    assert get_username(data['token']) == get_username(token)


async def test_socket_token_requires_app_token(client):
    resp = await client.post('/ws/token')
    assert resp.status == 403

    text = await resp.text()
    assert text == '403: Forbidden'


async def test_retrieves_app_token(client):
    resp = await client.post('/token', json={
        'username': 'test-user',
    })
    data = await resp.json()
    assert 'token' in data
    assert is_token_valid(data['token'], config.APP_SECRET) == True


async def test_passes_healthcheck(client):
    resp = await client.get('/healthcheck')
    assert resp.status == 200

    text = await resp.text()
    assert text == 'ok'
