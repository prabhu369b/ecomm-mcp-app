from urllib.parse import urlparse

from pydantic import AnyHttpUrl

from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from app.config.settings import get_settings
from app.modules.auth.oauth.scopes import PRODUCTS_READ
from app.modules.auth.token_service import TokenService
from app.modules.mcp.token_verifier import OAuthTokenVerifier

settings = get_settings()

_base_host = urlparse(settings.base_url).netloc

mcp_server = FastMCP(
    name="mcp-server",
    token_verifier=OAuthTokenVerifier(TokenService()),
    auth=AuthSettings(
        issuer_url=AnyHttpUrl(settings.base_url),
        resource_server_url=AnyHttpUrl(f"{settings.base_url}/mcp"),
        # Baseline for ANY MCP session, independent of the full scope menu in
        # SUPPORTED_SCOPES — each tool gates its own extra scope via
        # dependency.require_scope(), so this must not grow with every new
        # scope or every client would need to consent to all of them at once.
        required_scopes=[PRODUCTS_READ],
    ),
    # Public base_url host must be allow-listed or the DNS-rebinding-protection
    # middleware rejects it with 421 (e.g. an ngrok tunnel host).
    transport_security=TransportSecuritySettings(allowed_hosts=[_base_host]),
    # Mounted at "/mcp" in main.py, so relative to that mount the streamable
    # endpoint itself lives at root — this is NOT the externally-visible path.
    streamable_http_path="/",
)
