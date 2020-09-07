import pytest

from messaging.main import create_application


@pytest.fixture
async def client(aiohttp_client):
    app = create_application()
    messaging_client = await aiohttp_client(app)
    return messaging_client
