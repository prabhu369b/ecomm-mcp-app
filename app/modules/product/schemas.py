

from sys import flags

from pydantic import BaseModel


class ProductResponse(BaseModel):
    id: str
    name: str
    category_id: str
    price: float
    stock: int
    description: str

class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int