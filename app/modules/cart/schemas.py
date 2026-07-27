from pydantic import BaseModel, Field


class CartItemRequest(BaseModel):
    product_id: str
    qty: int = Field(gt=0)


class CartItemResponse(BaseModel):
    product_id: str
    name: str
    price: int
    qty: int
    subtotal: int


class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total: int