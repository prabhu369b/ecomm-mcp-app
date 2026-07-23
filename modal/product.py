from .common import MongoDocument
from bson import ObjectId
from pydantic import BaseModel

class Product(MongoDocument):
    name: str
    category_id: ObjectId
    price: int
    stock: int
    description: str


class ProductCreate(Product):
    pass

class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    stock: int | None = None
    category_id: str | None = None