from fastapi import Depends

from app.database.dependency import get_mongo, get_redis
from app.database.mongo import MongoService
from app.database.redis import RedisService
from app.modules.product_v2.repository import ProductV2Repository
from app.modules.product_v2.service import ProductV2Service


def get_product_v2_service(
    mongo: MongoService = Depends(get_mongo),
    redis: RedisService = Depends(get_redis),
) -> ProductV2Service:
    return ProductV2Service(ProductV2Repository(mongo), redis)
