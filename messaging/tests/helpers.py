from aiohttp.web import WebSocketResponse
from aiohttp.client import ClientSession


async def app_token(client: ClientSession) -> str:
    resp = await client.post('/token', json={
        'username': 'test-user',
    })
    data = await resp.json()
    token = data['token']
    return token


async def socket_token(client: ClientSession) -> str:
    token = await app_token(client)
    resp = await client.post('/ws/token', headers={
        'Authorization': token,
    })
    data = await resp.json()
    token = data['token']
    return token


async def ws_connect(client: ClientSession, token: str) -> WebSocketResponse:
    return await client.ws_connect(f'/ws?authorization={token}')
