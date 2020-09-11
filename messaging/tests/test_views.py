import jwt
import redis
from aiohttp.client_exceptions import WSServerHandshakeError

from messaging import config
from messaging.authentication import (
    get_user_id,
    is_token_valid,
)


async def test_establishes_and_closes_multiple_ws_connections(client):
    sockets = client.app['sockets']
    resp = await client.get('/token')
    data = await resp.json()
    token = data['token']

    resp = await client.get('/ws/token', headers={
        'Authorization': token,
    })
    data = await resp.json()
    token = data['token']

    user_id = get_user_id(token)
    ws1 = await client.ws_connect('/ws?token={}'.format(token))
    ws2 = await client.ws_connect('/ws?token={}'.format(token))

    await ws1.close()
    await ws1.receive()
    assert len(sockets.get_sockets(user_id)) == 1


##async def test_receives_downstream_message(client):
##    resp = await client.get('/token')
##    data = await resp.json()
##    token = data['token']
##
##    resp = await client.get('/ws/token', headers={
##        'Authorization': token,
##    })
##    data = await resp.json()
##    token = data['token']
##
##    user_id = get_user_id(token)
##    ws = await client.ws_connect('/ws?token={}'.format(token))
##
##    await notify(user_id, 'hello')
##    msg = await ws.receive()
##    assert msg.data == 'hello'


async def test_establishes_ws_connection(client):
    resp = await client.get('/token')
    data = await resp.json()
    token = data['token']

    resp = await client.get('/ws/token', headers={
        'Authorization': token,
    })
    data = await resp.json()
    token = data['token']

    ws = await client.ws_connect('/ws?token={}'.format(token))
    await ws.ping()

    await ws.send_str('hello world')
    msg = await ws.receive()
    assert msg.data == 'hello world'


async def test_fails_to_establish_ws_connection(client):
    try:
        await client.ws_connect('/ws?token=invalid-token')
    except WSServerHandshakeError as e:
        assert e.status == 403
    else:
        raise Exception('Handshake should not succeed')


async def test_retrieves_socket_token(client):
    resp = await client.get('/token')
    data = await resp.json()
    token = data['token']

    resp = await client.get('/ws/token', headers={
        'Authorization': token,
    })
    data = await resp.json()
    assert 'token' in data
    assert is_token_valid(data['token'], config.SOCKET_SECRET) == True
    assert get_user_id(data['token']) == get_user_id(token)


async def test_socket_token_requires_app_token(client):
    resp = await client.get('/ws/token')
    assert resp.status == 403

    text = await resp.text()
    assert text == '403: Forbidden'


async def test_retrieves_app_token(client):
    resp = await client.get('/token')
    data = await resp.json()
    assert 'token' in data
    assert is_token_valid(data['token'], config.APP_SECRET) == True


async def test_passes_healthcheck(client):
    resp = await client.get('/healthcheck')
    assert resp.status == 200

    text = await resp.text()
    assert text == 'ok'
