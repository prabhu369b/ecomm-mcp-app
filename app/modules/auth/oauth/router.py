from typing import Annotated, Literal
from urllib.parse import quote

from fastapi import APIRouter, Form, Request, status, Depends
from pydantic import HttpUrl
from app.modules.auth.dependency import get_current_user, get_optional_current_user
from app.modules.auth.schemas import AuthenticatedUser
from app.shared.response import ApiResponse
from app.shared.openapi import error_responses
from app.modules.auth.oauth.exceptions import AuthorizationRequestNotFound, InvalidClient, InvalidGrant, OAuthClientNotFound, InvalidRedirectUri, InvalidScope
from app.modules.auth.oauth.schemas import AuthorizationResult, ConsentApprovalResult, ConsentRequest, ConsentResponse, CreateOAuthClientRequest, CreateOAuthClientResponse, AuthorizationRequest, IntrospectionResponse, JWKSResponse, TokenRequest, TokenResponse
from app.modules.auth.oauth.dependencies import get_oauth_service
from app.modules.auth.oauth.oauth_service import OAuthService

router = APIRouter()

@router.post(
    "/clients",
    response_model=CreateOAuthClientResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_client(
    request: CreateOAuthClientRequest,
    service: OAuthService = Depends(get_oauth_service),
):
    # RFC 7591 dynamic client registration response — must be the raw client
    # metadata object at the top level, not wrapped in the app's ApiResponse
    # envelope, or Claude's MCP client (and any spec-compliant client) can't
    # parse client_id/client_secret out of it.
    return await service.register_client(request)

@router.get(
    "/authorize",
    response_model=AuthorizationResult,
    responses=error_responses(OAuthClientNotFound, InvalidRedirectUri, InvalidScope),
)
async def authorize(
    http_request: Request,
    request: AuthorizationRequest = Depends(),
    oauth_service: OAuthService = Depends(get_oauth_service),
    current_user: AuthenticatedUser | None = Depends(get_optional_current_user),
):
    result = await oauth_service.authorize(
        request,
        current_user
    )

    if current_user is None:
        result.login_url = (
            "/app/login?"
            f"request_id={result.request_id}&"
            f"next={quote(str(http_request.url))}"
        )

    return result


@router.get(
    "/authorize/consent",
    response_model=ApiResponse[ConsentResponse],
    responses=error_responses(AuthorizationRequestNotFound, OAuthClientNotFound),
)
async def authorize_consent(
    request_id: str,
    oauth_service: OAuthService = Depends(get_oauth_service),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    result = await oauth_service.get_consent(
        request_id=request_id,
        current_user=current_user,
    )

    return ApiResponse(
        success=True,
        message="Consent details retrieved successfully.",
        data=result,
    )


@router.post(
    "/authorize/consent",
    response_model=ApiResponse[ConsentApprovalResult],
    responses=error_responses(AuthorizationRequestNotFound, OAuthClientNotFound),
)
async def approve_consent(
    request: ConsentRequest,
    oauth_service: OAuthService = Depends(get_oauth_service),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    result = await oauth_service.approve_consent(
        request,
        current_user,
    )

    return ApiResponse(
        success=True,
        message="Consent decision recorded.",
        data=result,
    )


@router.post(
    "/token",
    response_model=TokenResponse,
    responses=error_responses(InvalidGrant, InvalidClient, OAuthClientNotFound),
)
async def token(
    # RFC 6749 §3.2: token requests are application/x-www-form-urlencoded, not
    # JSON, and the response is the raw token object at the top level.
    grant_type: Annotated[Literal["authorization_code"], Form()],
    code: Annotated[str, Form()],
    redirect_uri: Annotated[HttpUrl, Form()],
    client_id: Annotated[str, Form()],
    client_secret: Annotated[str | None, Form()] = None,
    code_verifier: Annotated[str | None, Form()] = None,
    oauth_service: OAuthService = Depends(get_oauth_service),
):
    request = TokenRequest(
        grant_type=grant_type,
        code=code,
        redirect_uri=redirect_uri,
        client_id=client_id,
        client_secret=client_secret,
        code_verifier=code_verifier,
    )

    return await oauth_service.exchange_token(request)


@router.post(
    "/introspect",
    response_model=IntrospectionResponse,
)
async def introspect(
    # RFC 7662 §2.1: introspection requests are also form-encoded.
    token: Annotated[str, Form()],
    oauth_service: OAuthService = Depends(get_oauth_service),
):
    return oauth_service.introspect_token(token)


@router.get(
    "/jwks",
    response_model=JWKSResponse,
)
async def jwks():
    # ponytail: tokens are signed HS256 (shared secret), no public key exists to publish.
    # Empty key set is the correct RFC7517 response until the service migrates to RS256.
    return JWKSResponse(keys=[])

