from mcp.server.auth.middleware.auth_context import get_access_token

from app.database.mongo import mongo
from app.modules.product.repository import ProductRepository
from app.core.logger import Logger

logger = Logger.get_logger(__name__)

product_repo = ProductRepository(mongo)


def require_scope(scope: str) -> None:
    access_token = get_access_token()
    if access_token is None or scope not in access_token.scopes:
        logger.warning(
            "mcp permission denied: required scope=%s client_id=%s",
            scope, access_token.client_id if access_token else None,
        )
        raise PermissionError(f"Missing required scope: {scope}")
