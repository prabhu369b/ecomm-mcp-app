from pydantic import BaseModel


class ProductResponse(BaseModel):
    id: str
    name: str
    category_id: str
    price: float
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


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
