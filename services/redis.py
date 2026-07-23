import redis as r
from redis.cache import CacheConfig
from config.settings import get_settings
from core.logger import Logger

logger = Logger.get_logger(__name__)


class RedisService: 
    def __init__(self):
        settings = get_settings()
        self.redis = r.Redis(host=settings.redis.host, port=settings.redis.port, decode_responses=True, cache_config=CacheConfig())
        try:
            self.redis.ping()
            logger.info("Redis Connected")
        except ConnectionError:
            logger.exception("Failed to connect to Redis")
            raise
    def close(self):
        if(self.redis is not None):
            self.redis.close()
            logger.info("Redis Closed")

redis = RedisService()