from app.modules.product.models import Product
from app.database.mongo import MongoService


class ProductRepository:

    def __init__(self, mongo: MongoService):
        self.collection = mongo.db.products

    def list_all(self, limit: int = 50) -> list[Product]:
        documents = self.collection.find().limit(limit)
        return [self._to_product(doc) for doc in documents]

    @staticmethod
    def _to_product(doc: dict) -> Product:
        doc["id"] = str(doc.pop("_id"))
        doc["category_id"] = str(doc["category_id"])
        return Product(**doc)
