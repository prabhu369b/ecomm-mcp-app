from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.logger import Logger

Logger.configure()

from services.redis import redis
from services.mongo import mongo

@asynccontextmanager
async def lifespan(app = FastAPI):

    logger = Logger.get_logger(__name__)
    logger.info("Application Started")

    app.state.redis = redis
    app.state.mongo = mongo

   
    yield
    
    redis.close()
    mongo.close()

    logger.info("Application Stopped")
