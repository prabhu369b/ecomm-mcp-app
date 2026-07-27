from fastapi import Depends

from app.database.dependency import get_mongo, get_redis
from app.database.lock import RedisLockService
from app.database.mongo import MongoService
from app.database.redis import RedisService
from app.modules.cart.repository import CartRepository
from app.modules.order.repository import OrderRepository
from app.modules.order.service import OrderService
from app.modules.product.repository import ProductRepository

def get_order_service(
    mongo: MongoService = Depends(get_mongo),
    redis: RedisService = Depends(get_redis)
) -> OrderService:
    return OrderService(
       OrderRepository(mongo),
       CartRepository(redis),
       ProductRepository(mongo),
       RedisLockService(redis)
    )