from mcp.server.auth.provider import AccessToken, TokenVerifier

from app.modules.auth.exceptions import AccessTokenExpired, InvalidAccessToken
from app.modules.auth.token_service import TokenService


class OAuthTokenVerifier(TokenVerifier):
    """Verifies MCP bearer tokens against the app's own OAuth-issued JWTs."""

    def __init__(self, token_service: TokenService):
        self.token_service = token_service

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            payload = self.token_service.verify_access_token(token)
        except (AccessTokenExpired, InvalidAccessToken):
            return None

        return AccessToken(
            token=token,
            client_id=payload.client_id or "",
            scopes=payload.scope.split() if payload.scope else [],
            expires_at=int(payload.exp.timestamp()),
            subject=payload.sub,
        )
