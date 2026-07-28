from bson import ObjectId
from app.database.mongo import MongoService
from app.modules.order.models import Order
from app.core.logger import Logger

logger = Logger.get_logger(__name__)


class OrderRepository:
    def __init__(self, mongo: MongoService) -> None:
        self.collection = mongo.db.orders

    def create(self, order: Order) -> Order:
        doc = order.model_dump(exclude={"id"})
        result = self.collection.insert_one(doc)
        logger.info("order created: order_id=%s user_id=%s total=%s", result.inserted_id, order.user_id, order.total)
        return order.model_copy(update={"id": str(result.inserted_id)})

    def find_by_id(self, order_id: str, user_id: str) -> Order | None:
        doc = self.collection.find_one({"_id": ObjectId(order_id), "user_id": user_id})
        if doc is None:
            return None
        return self._to_order(doc)

    def list_by_user(self, user_id: str, page: int, page_size: int) -> tuple[list[Order], int]:
        filt = {"user_id": user_id}
        total = self.collection.count_documents(filt)
        skip = (page - 1) * page_size
        docs = self.collection.find(filt).sort("created_at", -1).skip(skip).limit(page_size)
        return [self._to_order(d) for d in docs], total

    @staticmethod
    def _to_order(doc: dict) -> Order:
        doc["id"] = str(doc.pop("_id"))
        return Order(**doc)