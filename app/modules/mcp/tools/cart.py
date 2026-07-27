from app.modules.auth.oauth.scopes import CART_READ, CART_WRITE
from app.modules.mcp.dependency import cart_service, current_user_id, require_scope
from app.modules.mcp.instance import mcp_server
from app.core.logger import Logger

logger = Logger.get_logger(__name__)


@mcp_server.tool()
async def view_cart() -> dict:
    """View the current user's cart contents and total."""
    require_scope(CART_READ)
    user_id = current_user_id()

    logger.info("mcp tool call: view_cart user_id=%s", user_id)

    cart = await cart_service.get(user_id)
    return cart.model_dump()


@mcp_server.tool()
async def add_to_cart(product_id: str, qty: int = 1) -> dict:
    """Add a product to the current user's cart (or increase its quantity)."""
    require_scope(CART_WRITE)
    user_id = current_user_id()

    logger.info("mcp tool call: add_to_cart user_id=%s product_id=%s qty=%s", user_id, product_id, qty)

    cart = await cart_service.add_item(user_id, product_id, qty)
    return cart.model_dump()
