import jwt

from messaging import config


async def test_establishes_connection(client):
    resp = await client.get('/token')
    data = await resp.json()
    token = data['token']

    resp = await client.get('/connect', headers={
        'Authorization': token,
    })
    text = await resp.text()
    assert text == 'ok'


async def test_returns_auth_error(client):
    resp = await client.get('/connect')
    assert resp.status == 403

    text = await resp.text()
    assert text == '403: Forbidden'


async def test_retrieves_jwt_token(client):
    resp = await client.get('/token')
    data = await resp.json()
    assert 'token' in data

    token = str.encode(data['token'])
    decoded = jwt.decode(token, config.SECRET, algorithm=[config.JWT_ALG])
    assert decoded == {}


async def test_passes_healthcheck(client):
    resp = await client.get('/healthcheck')
    assert resp.status == 200

    text = await resp.text()
    assert text == 'ok'
