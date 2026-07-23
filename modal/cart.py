from .common import MongoDocument
from pydantic import BaseModel
from bson import ObjectId

class CartItem(BaseModel):
    product_id: ObjectId
    qty: int

class Cart(MongoDocument):
    user_id: str
    items: list[CartItem] = []