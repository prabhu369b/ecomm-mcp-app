from app.database.redis import RedisService
from app.modules.cart.models import Cart, CartItem
from app.modules.cart.keys import CartKeys

CART_TTL = 60 * 60 * 24 * 7  # 7 days

class CartRepository:
    def __init__(self, redis: RedisService) -> None:
        self.redis = redis

    async def get(self, user_id: str) -> Cart:
        raw = await self.redis.get(CartKeys.cart(user_id))
        if not raw:
            return Cart(user_id=user_id, items=[])
        return Cart.model_validate_json(raw)

    async def save(self, cart: Cart) -> None:
        await self.redis.set(CartKeys.cart(cart.user_id), cart.model_dump_json(), CART_TTL)

    async def clear(self, user_id: str) -> None:
        await self.redis.delete(CartKeys.cart(user_id))
    