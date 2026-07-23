from app.shared.common import MongoDocument
from pydantic import BaseModel
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    SHIPPED = "shipped"
    PAID = "paid"

class OrderItem(BaseModel):
    product_id: str
    name: str
    price: float
    qty: int

class Order(MongoDocument):
    user_id: str
    items: list[OrderItem]
    total: float
    status: OrderStatus = OrderStatus.PENDING
