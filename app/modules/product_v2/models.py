from app.shared.common import MongoDocument


class ProductV2(MongoDocument):
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
