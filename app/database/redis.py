import redis as r
from redis.cache import CacheConfig
from app.config.settings import get_settings
from app.core.logger import Logger

logger = Logger.get_logger(__name__)


class RedisService:
    def __init__(self):
        settings = get_settings()
        self.client = r.Redis(host=settings.redis.host, port=settings.redis.port, decode_responses=True, cache_config=CacheConfig())
        try:
            self.client.ping()
            logger.info("Redis Connected")
        except ConnectionError:
            logger.exception("Failed to connect to Redis")
            raise

    def close(self):
        self.client.close()
        logger.info("Redis Closed")


    def set(self, key, value, ttl):
        self.client.set(key, value, ex=ttl)
    
    def get(self, key):
        return self.client.get(key)

    def delete(self, key):
        self.client.delete(key)

redis = RedisService()