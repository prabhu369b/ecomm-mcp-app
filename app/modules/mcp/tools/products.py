from app.modules.auth.oauth.scopes import PRODUCTS_READ
from app.modules.mcp.dependency import product_repo, require_scope
from app.modules.mcp.instance import mcp_server
from app.modules.mcp.resources import PRODUCTS_RESOURCE_URI
from app.core.logger import Logger

logger = Logger.get_logger(__name__)


@mcp_server.tool(meta={"ui": {"resourceUri": PRODUCTS_RESOURCE_URI}})
def list_products(limit: int = 20) -> list[dict]:
    """List products from the store catalog."""
    require_scope(PRODUCTS_READ)

    logger.info("mcp tool call: list_products limit=%s", limit)

    return [
        product.model_dump()
        for product in product_repo.list_all(limit=limit)
    ]


@mcp_server.tool()
def search_products(
    q: str | None = None,
    category_id: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """Search the store catalog by name and/or category, paginated."""
    require_scope(PRODUCTS_READ)

    logger.info(
        "mcp tool call: search_products q=%s category_id=%s page=%s page_size=%s",
        q, category_id, page, page_size,
    )

    products, total = product_repo.search(q, category_id, page, page_size)

    return {
        "items": [product.model_dump() for product in products],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
