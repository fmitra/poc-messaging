import pytest

from messaging.main import create_application


@pytest.fixture
async def client(test_client):
    app = await test_client(create_application)
    return app
