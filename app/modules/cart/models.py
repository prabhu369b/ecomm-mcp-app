from app.shared.common import MongoDocument
from pydantic import BaseModel

class CartItem(BaseModel):
    product_id: str
    qty: int

class Cart(MongoDocument):
    user_id: str
    items: list[CartItem] = []