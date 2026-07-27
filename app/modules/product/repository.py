from os import name

from app.modules.product.models import Product
from app.database.mongo import MongoService


class ProductRepository:
    def __init__(self, mongo: MongoService):
        self.collection = mongo.db.products

    def list_all(self, limit: int = 50) -> list[Product]:
        documents = self.collection.find().limit(limit)
        return [self._to_product(doc) for doc in documents]

    def search(self, q: str | None = None, category_id: str | None = None, page: int = 1, page_size : int = 20) -> tuple[list[Product], int]:
        filt : dict = {}

        if q:
            filt["name"] = {"$regex": q, "$options": "i"}
        if category_id:
            filt["category_id"]=category_id
        total = self.collection.count_documents(filt)

        skip = (page - 1) * page_size
        documents = self.collection.find(filt).skip(skip).limit(page_size)
        return [self._to_product(doc) for doc in documents], total

    @staticmethod
    def _to_product(doc: dict) -> Product:
        doc["id"] = str(doc.pop("_id"))
        doc["category_id"] = str(doc["category_id"])
        return Product(**doc)
