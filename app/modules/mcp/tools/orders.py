from app.modules.auth.oauth.scopes import ORDERS_READ, ORDERS_WRITE
from app.modules.mcp.dependency import current_user_id, order_service, require_scope
from app.modules.mcp.instance import mcp_server
from app.core.logger import Logger

logger = Logger.get_logger(__name__)


@mcp_server.tool()
async def checkout() -> dict:
    """Check out the current user's cart, placing an order and clearing the cart."""
    require_scope(ORDERS_WRITE)
    user_id = current_user_id()

    logger.info("mcp tool call: checkout user_id=%s", user_id)

    order = await order_service.checkout(user_id)
    return order.model_dump()


@mcp_server.tool()
async def list_orders(page: int = 1, page_size: int = 20) -> dict:
    """List the current user's order history, paginated."""
    require_scope(ORDERS_READ)
    user_id = current_user_id()

    logger.info("mcp tool call: list_orders user_id=%s page=%s page_size=%s", user_id, page, page_size)

    orders = await order_service.list(user_id, page, page_size)
    return orders.model_dump()
