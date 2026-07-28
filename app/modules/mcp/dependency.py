from mcp.server.auth.middleware.auth_context import get_access_token

from app.config.settings import get_settings
from app.database.mongo import mongo
from app.database.redis import redis
from app.database.lock import RedisLockService
from app.modules.cart.repository import CartRepository
from app.modules.cart.service import CartService
from app.modules.order.repository import OrderRepository
from app.modules.order.service import OrderService
from app.modules.product.repository import ProductRepository
from app.modules.product_v2.repository import ProductV2Repository
from app.core.logger import Logger

logger = Logger.get_logger(__name__)

settings = get_settings()

# Which catalog schema the MCP tools read/write against. Controlled by
# settings.catalog_version ("v1" or "v2") so the whole MCP product/cart/order
# surface can switch without touching any tool code.
product_repo = ProductV2Repository(mongo) if settings.catalog_version == "v2" else ProductRepository(mongo)
logger.info("mcp product catalog active: version=%s", settings.catalog_version)

cart_repo = CartRepository(redis)
cart_service = CartService(cart_repo, product_repo)
order_service = OrderService(
    OrderRepository(mongo),
    cart_repo,
    product_repo,
    RedisLockService(redis),
)


def require_scope(scope: str) -> None:
    access_token = get_access_token()
    if access_token is None or scope not in access_token.scopes:
        logger.warning(
            "mcp permission denied: required scope=%s client_id=%s",
            scope, access_token.client_id if access_token else None,
        )
        raise PermissionError(f"Missing required scope: {scope}")


def current_user_id() -> str:
    access_token = get_access_token()
    if access_token is None or access_token.subject is None:
        raise PermissionError("Missing authenticated user")
    return access_token.subject
