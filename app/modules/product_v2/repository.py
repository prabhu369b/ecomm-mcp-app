from bson import ObjectId

from app.database.mongo import MongoService
from app.modules.product_v2.models import ProductV2
from app.core.logger import Logger

logger = Logger.get_logger(__name__)


class ProductV2Repository:
    def __init__(self, mongo: MongoService):
        self.collection = mongo.db.products_v2

    def list_all(self, limit: int = 50) -> list[ProductV2]:
        documents = self.collection.find().limit(limit)
        return [self._to_product(doc) for doc in documents]

    def search(
        self,
        q: str | None = None,
        category_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ProductV2], int]:
        filt: dict = {}

        if q:
            filt["name"] = {"$regex": q, "$options": "i"}
        if category_id:
            filt["category_id"] = category_id

        total = self.collection.count_documents(filt)

        skip = (page - 1) * page_size
        documents = self.collection.find(filt).skip(skip).limit(page_size)
        return [self._to_product(doc) for doc in documents], total

    def find_by_id(self, product_id: str) -> ProductV2 | None:
        try:
            doc = self.collection.find_one({"_id": ObjectId(product_id)})
        except Exception:
            logger.warning("product_v2 find_by_id failed: invalid id=%s", product_id)
            return None
        if doc is None:
            return None
        return self._to_product(doc)

    def decrement_stock(self, product_id: str, qty: int) -> None:
        self.collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$inc": {"stock": -qty}},
        )
        logger.info("product_v2 stock decremented: product_id=%s qty=%s", product_id, qty)

    @staticmethod
    def _to_product(doc: dict) -> ProductV2:
        doc["id"] = str(doc.pop("_id"))
        doc["category_id"] = str(doc["category_id"])
        return ProductV2(**doc)
