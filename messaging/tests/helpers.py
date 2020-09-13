from aiohttp.client import ClientSession


async def app_token(client: ClientSession) -> str:
    resp = await client.get('/token')
    data = await resp.json()
    token = data['token']
    return token


async def socket_token(client: ClientSession) -> str:
    token = await app_token(client)
    resp = await client.get('/ws/token', headers={
        'Authorization': token,
    })
    data = await resp.json()
    token = data['token']
    return token

