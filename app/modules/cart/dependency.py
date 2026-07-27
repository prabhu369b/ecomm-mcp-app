from fastapi import Depends
from app.database.dependency import get_mongo, get_redis
from app.database.mongo import MongoService
from app.database.redis import RedisService
from app.modules.cart.service import CartService
from app.modules.cart.repository import CartRepository
from app.modules.product.repository import ProductRepository

def get_cart_service(
    mongo: MongoService = Depends(get_mongo),
    redis: RedisService = Depends(get_redis),
) -> CartService:
    return CartService(CartRepository(redis), ProductRepository(mongo))