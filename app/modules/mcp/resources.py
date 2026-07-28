from pathlib import Path

from app.modules.mcp.instance import mcp_server
from app.core.logger import Logger

logger = Logger.get_logger(__name__)

RESOURCE_MIME_TYPE = "text/html;profile=mcp-app"

PRODUCTS_RESOURCE_URI = "ui://products/mcp-app.html"

_UI_DIST_DIR = Path(__file__).resolve().parents[3] / "ui" / "dist"


@mcp_server.resource(
    PRODUCTS_RESOURCE_URI,
    name="Products UI",
    mime_type=RESOURCE_MIME_TYPE,
)
def products_ui() -> str:
    html_path = _UI_DIST_DIR / "mcp-app.html"
    logger.info("mcp resource read: %s", PRODUCTS_RESOURCE_URI)
    return html_path.read_text()
