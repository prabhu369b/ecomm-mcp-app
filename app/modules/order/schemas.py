from pydantic import BaseModel
from app.modules.order.models import OrderStatus


class OrderItemResponse(BaseModel):
    product_id: str
    name: str
    price: float
    qty: int


class OrderResponse(BaseModel):
    id: str
    items: list[OrderItemResponse]
    total: float
    status: OrderStatus
    created_at: str


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    total: int
    page: int
    page_size: int