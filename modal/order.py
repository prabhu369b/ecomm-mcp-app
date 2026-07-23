from .common import MongoDocument
from pydantic import BaseModel
from enum import Enum
from bson import ObjectId

class OrderStatus(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    "SHIPPED" = "shipped"
    "PAID" = "paid"

class OrderItem(BaseModel):
    product_id: ObjectId
    name: str
    price: float
    qty: int

class Order(MongoDocument):
    user_id: ObjectId
    items: list[OrderItem]
    total: float
    status: OrderStatus = OrderStatus.PENDING
    