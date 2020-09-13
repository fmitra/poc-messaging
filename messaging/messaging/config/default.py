from typing import TypedDict


class RedisConfig(TypedDict):
    """redis-py configuration settings."""
    host: str
    port: int
    db: int
    password: str


DEBUG = True

APP_SECRET = 'QxrY57HvDUAIZQvzAQgAe1zGlIR3Fp25sgphsY+1V0tUEQ9efzLeAw'
SOCKET_SECRET = 'oQhx7CPs+fe3s47BY1Tf/RnoeMBzT+MyFrG0sjxr'

JWT_ALG = 'HS256'

REDIS: RedisConfig = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'password': 'swordfish',
}
