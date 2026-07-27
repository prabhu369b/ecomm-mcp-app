import redis.asyncio as r
from app.config.settings import get_settings
from app.core.logger import Logger

logger = Logger.get_logger(__name__)


class RedisService:
    def __init__(self):
        settings = get_settings()
        self.client = r.Redis(host=settings.redis.host, port=settings.redis.port, decode_responses=True)

    async def connect(self):
        try:
            await self.client.ping()
            logger.info("Redis Connected")
        except ConnectionError:
            logger.exception("Failed to connect to Redis")
            raise

    async def close(self):
        await self.client.close()
        logger.info("Redis Closed")


    async def set(self, key, value, ttl):
        await self.client.set(key, value, ex=ttl)

    async def get(self, key):
        return await self.client.get(key)

    async def delete(self, key):
        await self.client.delete(key)

    def pipeline(self):
        # client.pipeline() is sync — it just builds the Pipeline object, no I/O yet.
        return self.client.pipeline(transaction=True)

    def lock(self, key, timeout=10, blocking_timeout=5):
        # Swap to Redlock only if you run multiple independent Redis masters.
        return self.client.lock(f"lock:{key}", timeout=timeout, blocking_timeout=blocking_timeout)

redis = RedisService()