from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.logger import Logger

Logger.configure()

from app.database.redis import redis
from app.database.mongo import mongo

@asynccontextmanager
async def lifespan(app = FastAPI):

    logger = Logger.get_logger(__name__)
    logger.info("Application Started")

    mongo.client  # force-connect now instead of on first request

    app.state.redis = redis
    app.state.mongo = mongo

    yield
    
    redis.close()
    mongo.close()

    logger.info("Application Stopped")
