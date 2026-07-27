from app.modules.auth.oauth.scopes import PRODUCTS_READ
from app.modules.mcp.dependency import product_repo, require_scope
from app.modules.mcp.instance import mcp_server
from app.core.logger import Logger

logger = Logger.get_logger(__name__)


@mcp_server.tool()
def list_products(limit: int = 20) -> list[dict]:
    """List products from the store catalog."""
    require_scope(PRODUCTS_READ)

    logger.info("mcp tool call: list_products limit=%s", limit)

    return [
        product.model_dump()
        for product in product_repo.list_all(limit=limit)
    ]
