from urllib.parse import urlparse

from pydantic import AnyHttpUrl

from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from app.config.settings import get_settings
from app.database.mongo import mongo
from app.modules.auth.oauth.scopes import PRODUCTS_READ, SUPPORTED_SCOPES
from app.modules.auth.token_service import TokenService
from app.modules.mcp.token_verifier import OAuthTokenVerifier
from app.modules.product.repository import ProductRepository

settings = get_settings()

_base_host = urlparse(settings.base_url).netloc

mcp_server = FastMCP(
    name="mcp-server",
    token_verifier=OAuthTokenVerifier(TokenService()),
    auth=AuthSettings(
        issuer_url=AnyHttpUrl(settings.base_url),
        resource_server_url=AnyHttpUrl(f"{settings.base_url}/mcp"),
        required_scopes=SUPPORTED_SCOPES,
    ),
    # Public base_url host must be allow-listed or the DNS-rebinding-protection
    # middleware rejects it with 421 (e.g. an ngrok tunnel host).
    transport_security=TransportSecuritySettings(allowed_hosts=[_base_host]),
    # Mounted at "/mcp" in main.py, so relative to that mount the streamable
    # endpoint itself lives at root — this is NOT the externally-visible path.
    streamable_http_path="/",
)

product_repo = ProductRepository(mongo)


def _require_scope(scope: str) -> None:
    access_token = get_access_token()
    if access_token is None or scope not in access_token.scopes:
        raise PermissionError(f"Missing required scope: {scope}")


@mcp_server.tool()
def list_products(limit: int = 20) -> list[dict]:
    """List products from the store catalog."""
    _require_scope(PRODUCTS_READ)

    return [
        product.model_dump()
        for product in product_repo.list_all(limit=limit)
    ]
