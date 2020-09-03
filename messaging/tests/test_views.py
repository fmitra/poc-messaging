async def test_passes_healthcheck(client):
    resp = await client.get('/healthcheck')
    assert resp.status == 200

    text = await resp.text()
    assert text == 'ok'
