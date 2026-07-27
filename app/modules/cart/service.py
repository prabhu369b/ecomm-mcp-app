

from app.modules.cart.exceptions import InsufficientStock, ProductNotFound
from app.modules.cart.models import Cart, CartItem
from app.modules.cart.repository import CartRepository
from app.modules.cart.schemas import CartItemResponse, CartResponse
from app.modules.product.repository import ProductRepository


class CartService:
    def __init__(self, repo: CartRepository, product_repo: ProductRepository) -> None:
        self.repo = repo
        self.product_repo = product_repo

    async def _to_response(self, cart: Cart) -> CartResponse:
        items = []
        total = 0
        for item in cart.items:
            product = self.product_repo.find_by_id(item.product_id)

            if product is None:
                continue
            subtotal = product.price * item.qty
            total += subtotal

            items.append(CartItemResponse(
                product_id=item.product_id,
                name=product.name,
                price=product.price,
                qty=item.qty,
                subtotal=subtotal
            ))
        return CartResponse(items=items, total=total)

    async def get(self, user_id: str) -> CartResponse:
        return await self._to_response(await self.repo.get(user_id))

    async def add_item(self, user_id: str, product_id: str, qty: int) -> CartResponse:

        product = self.product_repo.find_by_id(product_id)
        if product is None:
            raise ProductNotFound()
        cart = await self.repo.get(user_id)

        existing = next((i for i in cart.items if i.product_id == product_id), None)
        new_qty = (existing.qty if existing else 0) + qty
        if new_qty > product.stock:
            raise InsufficientStock()
        if existing: 
            existing.qty = new_qty
        else:
            cart.items.append(CartItem(product_id=product_id, qty=qty))
        await self.repo.save(cart)

        return await self._to_response(cart)

    async def update_item(self, user_id: str, product_id: str, qty: int) -> CartResponse:
        cart = await self.repo.get(user_id)
        cart.items = [i for i in cart.items if i.product_id!=product_id]
        if qty > 0:
            cart.items.append(CartItem(product_id=product_id, qty=qty))
        await self.repo.save(cart)
        return await self._to_response(cart)

    async def remove_item(self, user_id: str, product_id: str) -> CartResponse:
        return await self.update_item(user_id, product_id, 0)

    async def clear(self, user_id: str) -> None:
        await self.repo.clear(user_id)
