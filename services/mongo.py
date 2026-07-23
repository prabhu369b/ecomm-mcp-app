from pymongo import MongoClient
from config.settings import get_settings
from core.logger import Logger

logger = Logger.get_logger(__name__)

class MongoService:
    def __init__(self):
        settings = get_settings()
        self.client = MongoClient(settings.mongo.url)
        self.db = self.client[settings.mongo.db_name]
        try:
            self.client.admin.command('ping')
            logger.info("Mongo Connected")
        except Exception:
            logger.exception("Failed to connect to Mongo")

    def close(self):
        if self.client:
            self.client.close()
            logger.info("Mongo Disconnected")

mongo = MongoService()