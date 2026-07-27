from typing import Literal

from pydantic import BaseModel, HttpUrl, Field, AliasChoices
from app.modules.auth.oauth.models import OAuthClient
from app.modules.auth.oauth.scopes import SUPPORTED_SCOPES

class CreateOAuthClientRequest(BaseModel):
    name: str = Field(
        min_length=3,
        max_length=100,
        default="MCP Client",
        validation_alias=AliasChoices("name", "client_name"),
    )
    redirect_uris: list[HttpUrl]
    allowed_scopes: list[str] = Field(default_factory=lambda: list(SUPPORTED_SCOPES))
    is_confidential: bool = True
    token_endpoint_auth_method: Literal["client_secret_post", "none"] | None = None

class CreateOAuthClientResponse(BaseModel):
    client_id: str
    client_secret: str | None = None
    client_id_issued_at: int
    client_secret_expires_at: int = 0
    redirect_uris: list[HttpUrl]
    grant_types: list[str] = ["authorization_code"]
    response_types: list[str] = ["code"]
    token_endpoint_auth_method: str

from typing import Literal

from pydantic import BaseModel, HttpUrl, Field


class AuthorizationRequest(BaseModel):

    response_type: Literal["code"]
    request_id: str | None = None
    client_id: str = Field(min_length=1)
    redirect_uri: HttpUrl
    scope: str = Field(
        default="",
        description="Space separated scopes"
    )
    state: str | None = Field(
        default=None,
        min_length=8,
        description="CSRF protection (RECOMMENDED, not all clients send it)"
    )
    code_challenge: str | None = None
    code_challenge_method: Literal["S256"] | None = None
    resource: str | None = Field(
        default=None,
        description="RFC 8707 resource indicator, accepted but not yet enforced"
    )

    @property
    def scopes(self) -> list[str]:
        return self.scope.split()

class AuthorizationResult(BaseModel):

    action: Literal["login","consent"]
    request_id: str | None
    client_name: str | None = None
    scopes: list[str] = []
    state: str | None = None
    login_url: str | None = None

class ConsentRequest(BaseModel):
    request_id: str
    approved: bool

class ConsentResponse(BaseModel):
    client_name: str
    scopes: list[str]

class ConsentApprovalResult(BaseModel):
    redirect_uri: str

class TokenRequest(BaseModel):
    grant_type: Literal["authorization_code"]
    code: str
    redirect_uri: HttpUrl
    client_id: str
    client_secret: str | None = None
    code_verifier: str | None = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["Bearer"]
    expires_in: int
    refresh_token: str | None = None
    scope: str

class AuthorizationServerMetadata(BaseModel):
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    registration_endpoint: str
    introspection_endpoint: str
    jwks_uri: str
    grant_types_supported: list[str] = ["authorization_code"]
    response_types_supported: list[str] = ["code"]
    code_challenge_methods_supported: list[str] = ["S256"]
    scopes_supported: list[str] = list(SUPPORTED_SCOPES)
    token_endpoint_auth_methods_supported: list[str] = ["client_secret_post", "none"]

class IntrospectionResponse(BaseModel):
    active: bool
    sub: str | None = None
    iss: str | None = None
    aud: str | None = None
    iat: int | None = None
    exp: int | None = None
    scope: str | None = None
    client_id: str | None = None
    token_type: Literal["Bearer"] | None = None

class JWK(BaseModel):
    kty: str
    use: str
    kid: str
    alg: str

class JWKSResponse(BaseModel):
    keys: list[JWK] = []