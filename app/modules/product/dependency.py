
from fastapi import Depends

from app.database.dependency import get_mongo, get_redis
from app.database.mongo import MongoService
from app.database.redis import RedisService
from app.modules.product.repository import ProductRepository
from app.modules.product.service import ProductService


def get_product_service(
        mongo: MongoService = Depends(get_mongo),
        redis: RedisService = Depends(get_redis)
) -> ProductService:

    return ProductService(ProductRepository(mongo), redis)