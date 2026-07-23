from .common import MongoDocument
from pydantic import BaseModel

class Category(MongoDocument):
    name: str
    slug: str

class CategoryCreate(BaseModel):
    name: str
    slug: str

