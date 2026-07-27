from app.database.redis import RedisService
from app.database.lock import RedisLockService
from app.modules.cart.repository import CartRepository
from app.modules.order.exceptions import EmptyCart, OrderNotFound
from app.modules.order.models import Order, OrderItem
from app.modules.order.repository import OrderRepository
from app.modules.order.schemas import OrderItemResponse, OrderListResponse, OrderResponse
from app.modules.product.repository import ProductRepository


class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        cart_repo: CartRepository,
        product_repo: ProductRepository,
        lock_service: RedisLockService,
    ):
        self.order_repo = order_repo
        self.cart_repo = cart_repo
        self.product_repo = product_repo
        self.lock_service = lock_service

    async def checkout(self, user_id: str) -> OrderResponse:
        async with self.lock_service.acquire(f"checkout:{user_id}"):
            cart = await self.cart_repo.get(user_id)
            if not cart.items:
                raise EmptyCart()

            order_items = []
            total = 0.0
            for item in cart.items:
                product = self.product_repo.find_by_id(item.product_id)
                if product is None or product.stock < item.qty:
                    raise EmptyCart()  # or a dedicated OutOfStock exception — your call
                order_items.append(OrderItem(
                    product_id=item.product_id, name=product.name,
                    price=product.price, qty=item.qty,
                ))
                total += product.price * item.qty
                self.product_repo.decrement_stock(item.product_id, item.qty)  # add this method

            order = self.order_repo.create(Order(user_id=user_id, items=order_items, total=total))
            await self.cart_repo.clear(user_id)

            return self._to_response(order)

    async def get(self, user_id: str, order_id: str) -> OrderResponse:
        order = self.order_repo.find_by_id(order_id, user_id)
        if order is None:
            raise OrderNotFound()
        return self._to_response(order)

    async def list(self, user_id: str, page: int, page_size: int) -> OrderListResponse:
        orders, total = self.order_repo.list_by_user(user_id, page, page_size)
        return OrderListResponse(
            items=[self._to_response(o) for o in orders], total=total, page=page, page_size=page_size,
        )

    @staticmethod
    def _to_response(order: Order) -> OrderResponse:
        return OrderResponse(
            id=str(order.id), 
            items=[OrderItemResponse(**i.model_dump()) for i in order.items],
            total=order.total,
            status=order.status,
            created_at=order.created_at.isoformat(),
        )