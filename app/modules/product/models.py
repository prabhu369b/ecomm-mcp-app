from app.shared.common import MongoDocument
from pydantic import BaseModel

class Product(MongoDocument):
    name: str
    category_id: str
    price: int
    stock: int
    description: str

    brand: str | None = None
    sku: str | None = None
    rating: float | None = None
    discount_percentage: float | None = None
    tags: list[str] = []
    thumbnail: str | None = None
    images: list[str] = []
    warranty_information: str | None = None
    shipping_information: str | None = None
    return_policy: str | None = None
    minimum_order_quantity: int | None = None


class ProductCreate(Product):
    pass

class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    stock: int | None = None
    category_id: str | None = None