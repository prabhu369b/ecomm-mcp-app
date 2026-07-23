from functools import cached_property
import redis as r
from redis.cache import CacheConfig
from app.config.settings import get_settings
from app.core.logger import Logger

logger = Logger.get_logger(__name__)


class RedisService:
    @cached_property
    def redis(self) -> r.Redis:
        settings = get_settings()
        client = r.Redis(host=settings.redis.host, port=settings.redis.port, decode_responses=True, cache_config=CacheConfig())
        try:
            client.ping()
            logger.info("Redis Connected")
        except ConnectionError:
            logger.exception("Failed to connect to Redis")
            raise
        return client

    def close(self):
        if "redis" in self.__dict__:
            self.redis.close()
            logger.info("Redis Closed")

redis = RedisService()