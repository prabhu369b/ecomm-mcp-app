from mcp.server.auth.middleware.auth_context import get_access_token

from app.database.mongo import mongo
from app.database.redis import redis
from app.modules.cart.repository import CartRepository
from app.modules.cart.service import CartService
from app.modules.product.repository import ProductRepository
from app.core.logger import Logger

logger = Logger.get_logger(__name__)

product_repo = ProductRepository(mongo)
cart_repo = CartRepository(redis)
cart_service = CartService(cart_repo, product_repo)


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
