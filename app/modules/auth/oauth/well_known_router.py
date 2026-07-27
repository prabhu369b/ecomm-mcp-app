from fastapi import APIRouter
from mcp.server.auth.routes import create_protected_resource_routes
from pydantic import AnyHttpUrl

from app.config.settings import get_settings
from app.modules.auth.oauth.scopes import SUPPORTED_SCOPES
from app.modules.auth.oauth.schemas import AuthorizationServerMetadata

router = APIRouter()

settings = get_settings()

# Registered directly on the main app's root router (not nested inside the
# "/mcp" mount) so it lands at the RFC 9728-mandated path regardless of
# where the actual MCP streamable endpoint is mounted.
router.routes.extend(
    create_protected_resource_routes(
        resource_url=AnyHttpUrl(f"{settings.base_url.rstrip('/')}/mcp"),
        authorization_servers=[AnyHttpUrl(settings.base_url)],
        scopes_supported=SUPPORTED_SCOPES,
    )
)


@router.get(
    "/.well-known/oauth-authorization-server",
    response_model=AuthorizationServerMetadata,
)
async def oauth_authorization_server_metadata():
    # Must match AnyHttpUrl(settings.base_url) exactly (mcp.server.auth issuer_url) —
    # clients string-compare this against protected-resource authorization_servers,
    # and AnyHttpUrl normalizes a bare host to a trailing slash.
    issuer = str(AnyHttpUrl(settings.base_url))
    base = issuer.rstrip("/")

    return AuthorizationServerMetadata(
        issuer=issuer,
        # The SPA page (web/src/pages/authorize), not the bare JSON API route —
        # it's what actually redirects an unauthenticated browser to /app/login
        # and renders the consent screen. Pointing this at /oauth/authorize
        # directly leaves a browser staring at raw JSON.
        authorization_endpoint=f"{base}/app/authorize",
        token_endpoint=f"{base}/oauth/token",
        registration_endpoint=f"{base}/oauth/clients",
        introspection_endpoint=f"{base}/oauth/introspect",
        jwks_uri=f"{base}/oauth/jwks",
    )
