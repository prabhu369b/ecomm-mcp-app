from app.database.redis import RedisService

class RedisLockService:

    def __init__(self, redis: RedisService):
        self.redis = redis

    def acquire(self, key: str, timeout: int = 10, blocking_timeout: int = 5):
        return self.redis.lock(key, timeout=timeout, blocking_timeout=blocking_timeout)
