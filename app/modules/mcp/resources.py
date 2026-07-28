from pathlib import Path

from app.config.settings import get_settings
from app.modules.mcp.instance import mcp_server
from app.core.logger import Logger

logger = Logger.get_logger(__name__)

settings = get_settings()

RESOURCE_MIME_TYPE = "text/html;profile=mcp-app"

PRODUCTS_RESOURCE_URI = "ui://products/mcp-app.html"

_UI_DIST_DIR = Path(__file__).resolve().parents[3] / "ui" / "dist"

# The MCP App runs in a sandboxed iframe with no same-origin server — any
# origin the UI loads resources from (product thumbnails, in this case)
# must be explicitly allow-listed or the host's CSP silently blocks them.
_resource_domains = [settings.catalog_image_domain] if settings.catalog_image_domain else []


@mcp_server.resource(
    PRODUCTS_RESOURCE_URI,
    name="Products UI",
    mime_type=RESOURCE_MIME_TYPE,
    meta={"ui": {"csp": {"resourceDomains": _resource_domains}}},
)
def products_ui() -> str:
    html_path = _UI_DIST_DIR / "mcp-app.html"
    logger.info("mcp resource read: %s", PRODUCTS_RESOURCE_URI)
    return html_path.read_text()
