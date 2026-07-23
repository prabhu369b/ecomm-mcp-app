from functools import cached_property
from pymongo import MongoClient
from app.config.settings import get_settings
from app.core.logger import Logger

logger = Logger.get_logger(__name__)

class MongoService:
    @cached_property
    def client(self) -> MongoClient:
        settings = get_settings()
        client = MongoClient(settings.mongo.url)
        try:
            client.admin.command('ping')
            logger.info("Mongo Connected")
        except Exception:
            logger.exception("Failed to connect to Mongo")
        return client

    @cached_property
    def db(self):
        settings = get_settings()
        return self.client[settings.mongo.db_name]

    def close(self):
        if "client" in self.__dict__:
            self.client.close()
            logger.info("Mongo Disconnected")

mongo = MongoService()