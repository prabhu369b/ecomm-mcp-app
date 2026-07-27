import base64
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode, urlsplit, urlunsplit
from app.modules.auth.oauth.authorization_code.repository import AuthorizationCodeRepository
from app.modules.auth.oauth.client_repository import OAuthRepository
from app.modules.auth.oauth.exceptions import AuthorizationRequestNotFound, InvalidClient, InvalidGrant, InvalidRedirectUri, InvalidScope, OAuthClientNotFound
from app.modules.auth.password import PasswordService
from app.modules.auth.oauth.request_repository.repository import AuthorizationRequestRepository
from app.modules.auth.oauth.schemas import AuthorizationRequest, AuthorizationResult, ConsentApprovalResult, ConsentRequest, ConsentResponse, CreateOAuthClientRequest, CreateOAuthClientResponse, IntrospectionResponse, TokenRequest, TokenResponse
from app.modules.auth.oauth.models import AuthorizationCode, OAuthClient
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.auth.exceptions import AccessTokenExpired, InvalidAccessToken
from app.modules.auth.token_service import TokenService
from app.core.utils.id_generator import IdGenerator
from app.config.settings import get_settings
from app.core.logger import Logger

settings = get_settings()
logger = Logger.get_logger(__name__)

class OAuthService:

    def __init__(
        self,
        client_repo: OAuthRepository,
        authorization_code_repo: AuthorizationCodeRepository,
        request_repo: AuthorizationRequestRepository,
        password_service: PasswordService,
        token_service: TokenService,
    ) -> None:

        self.client_repo = client_repo
        self.authorization_code_repo = authorization_code_repo
        self.request_repo = request_repo
        self.password_service = password_service
        self.token_service = token_service

    async def register_client(self, request: CreateOAuthClientRequest) -> CreateOAuthClientResponse:

        is_confidential = (
            request.token_endpoint_auth_method != "none"
            if request.token_endpoint_auth_method is not None
            else request.is_confidential
        )

        client_id = secrets.token_urlsafe(24)
        client_secret = secrets.token_urlsafe(48) if is_confidential else None

        client_secret_hash = (
            self.password_service.hash(client_secret) if client_secret else ""
        )

        now = datetime.now(timezone.utc)

        client = OAuthClient(
            name=request.name,
            client_id=client_id,
            client_secret_hash=client_secret_hash,
            redirect_urls=request.redirect_uris,
            allowed_scopes=request.allowed_scopes,
            grant_types=["authorization_code"],
            response_types=["code"],
            is_confidential=is_confidential,
            created_at=now,
            updated_at=now,
        )

        await self.client_repo.create(client)

        logger.info("registered oauth client: client_id=%s name=%s redirect_uris=%s", client_id, request.name, request.redirect_uris)

        return CreateOAuthClientResponse(
            client_id=client_id,
            client_secret=client_secret,
            client_id_issued_at=int(now.timestamp()),
            redirect_uris=request.redirect_uris,
            token_endpoint_auth_method="none" if not is_confidential else "client_secret_post",
        )

    async def authorize(
            self,
            request : AuthorizationRequest,
            current_user:AuthenticatedUser | None
    ) -> AuthorizationResult:
        logger.info(
            "authorize request: client_id=%s redirect_uri=%s scopes=%s user=%s",
            request.client_id, request.redirect_uri, request.scope,
            current_user.user_id if current_user else None,
        )

        client = await self.client_repo.find_client_by_id(request.client_id)
        if not client:
            logger.warning("authorize failed: unknown client_id=%s", request.client_id)
            raise OAuthClientNotFound()

        if request.redirect_uri not in client.redirect_urls:
            logger.warning(
                "authorize failed: redirect_uri=%s not registered for client_id=%s (allowed=%s)",
                request.redirect_uri, request.client_id, client.redirect_urls,
            )
            raise InvalidRedirectUri()

        self._validate_scopes(
            allowed=client.allowed_scopes,
            requested=request.scopes
        )

        if current_user and request.request_id:
            request_id = request.request_id
        else:
            request_id = IdGenerator.request_id()
            await self.request_repo.create(request_id, request)

        action = 'login' if current_user is None else 'consent'
        logger.info("authorize result: request_id=%s action=%s client_id=%s", request_id, action, client.client_id)

        return AuthorizationResult(
            action=action,
            request_id=request_id,
            client_name=client.name,
            scopes=request.scopes,
            state=request.state,
        )

    async def get_consent(
        self,
        request_id: str,
        current_user: AuthenticatedUser,
    ) -> ConsentResponse:

        request = await self.request_repo.find(request_id)

        if request is None:
            logger.warning("get_consent failed: request_id=%s not found/expired", request_id)
            raise AuthorizationRequestNotFound()

        client = await self.client_repo.find_client_by_id(request.client_id)
        if not client:
            logger.warning("get_consent failed: unknown client_id=%s for request_id=%s", request.client_id, request_id)
            raise OAuthClientNotFound()

        logger.info("get_consent: request_id=%s client_id=%s user=%s", request_id, client.client_id, current_user.user_id)

        return ConsentResponse(
            client_name=client.name,
            scopes=request.scopes,
        )

    async def approve_consent(
        self,
        request: ConsentRequest,
        current_user: AuthenticatedUser,
    ) -> ConsentApprovalResult:

        auth_request = await self.request_repo.find(request.request_id)

        if auth_request is None:
            logger.warning("approve_consent failed: request_id=%s not found/expired", request.request_id)
            raise AuthorizationRequestNotFound()

        client = await self.client_repo.find_client_by_id(auth_request.client_id)
        if not client:
            logger.warning("approve_consent failed: unknown client_id=%s", auth_request.client_id)
            raise OAuthClientNotFound()

        await self.request_repo.delete(request.request_id)

        if not request.approved:
            logger.info("approve_consent: request_id=%s denied by user=%s", request.request_id, current_user.user_id)
            redirect_uri = self._build_redirect_uri(
                str(auth_request.redirect_uri),
                error="access_denied",
                state=auth_request.state,
            )
            return ConsentApprovalResult(redirect_uri=redirect_uri)

        code = await self.create_authorization_code(
            client=client,
            user_id=current_user.user_id,
            redirect_uri=str(auth_request.redirect_uri),
            scopes=auth_request.scopes,
            code_challenge=auth_request.code_challenge,
            code_challenge_method=auth_request.code_challenge_method,
        )

        logger.info(
            "approve_consent: request_id=%s approved client_id=%s user=%s scopes=%s",
            request.request_id, client.client_id, current_user.user_id, auth_request.scopes,
        )

        redirect_uri = self._build_redirect_uri(
            str(auth_request.redirect_uri),
            code=code,
            state=auth_request.state,
        )

        return ConsentApprovalResult(redirect_uri=redirect_uri)

    async def create_authorization_code(
        self,
        *,
        client: OAuthClient,
        user_id: str,
        redirect_uri: str,
        scopes: list[str],
        code_challenge: str | None = None,
        code_challenge_method: str | None = None,
    ) -> str:

        code = secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc)
        authorization = AuthorizationCode(
           code=code,
           client_id=client.client_id,
           user_id=user_id,
           scopes=scopes,
           redirect_uri=redirect_uri,
           code_challenge=code_challenge,
           code_challenge_method=code_challenge_method,
           created_at=now,
           expires_at=now + timedelta(minutes=5)
        )

        await self.authorization_code_repo.create(authorization)

        return code

    async def exchange_token(
        self,
        request: TokenRequest,
    ) -> TokenResponse:

        logger.info("exchange_token request: client_id=%s redirect_uri=%s", request.client_id, request.redirect_uri)

        code = await self.authorization_code_repo.find(request.code)

        if not code:
            logger.warning("exchange_token failed: unknown/expired code for client_id=%s", request.client_id)
            raise InvalidGrant()

        if code.expires_at <= datetime.now(timezone.utc):
            logger.warning("exchange_token failed: code expired at=%s client_id=%s", code.expires_at, request.client_id)
            await self.authorization_code_repo.delete(request.code)
            raise InvalidGrant()

        if code.client_id != request.client_id:
            logger.warning("exchange_token failed: client_id mismatch code_client=%s request_client=%s", code.client_id, request.client_id)
            raise InvalidGrant()

        if code.redirect_uri != str(request.redirect_uri):
            logger.warning("exchange_token failed: redirect_uri mismatch code=%s request=%s", code.redirect_uri, request.redirect_uri)
            raise InvalidGrant()

        client = await self.client_repo.find_client_by_id(request.client_id)
        if not client:
            logger.warning("exchange_token failed: unknown client_id=%s", request.client_id)
            raise OAuthClientNotFound()

        if client.is_confidential:
            if not request.client_secret:
                logger.warning("exchange_token failed: missing client_secret for confidential client_id=%s", request.client_id)
                raise InvalidClient()
            try:
                self.password_service.verify(client.client_secret_hash, request.client_secret)
            except Exception:
                logger.warning("exchange_token failed: bad client_secret for client_id=%s", request.client_id)
                raise InvalidClient()

        self._verify_pkce(
            code_challenge=code.code_challenge,
            code_challenge_method=code.code_challenge_method,
            code_verifier=request.code_verifier,
        )

        await self.authorization_code_repo.delete(request.code)

        session_id = IdGenerator.session_id()

        access_token = self.token_service.create_access_token(
            user_id=code.user_id,
            session_id=session_id,
            scope=" ".join(code.scopes),
            client_id=code.client_id,
        )

        logger.info("exchange_token success: client_id=%s user_id=%s scopes=%s", code.client_id, code.user_id, code.scopes)

        return TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=settings.jwt.access_token_expiry,
            scope=" ".join(code.scopes),
        )

    def introspect_token(self, token: str) -> IntrospectionResponse:

        try:
            payload = self.token_service.verify_access_token(token)
        except (AccessTokenExpired, InvalidAccessToken):
            return IntrospectionResponse(active=False)

        return IntrospectionResponse(
            active=True,
            sub=payload.sub,
            iss=payload.iss,
            aud=payload.aud,
            iat=int(payload.iat.timestamp()),
            exp=int(payload.exp.timestamp()),
            scope=payload.scope,
            client_id=payload.client_id,
            token_type="Bearer",
        )

    def _verify_pkce(
        self,
        *,
        code_challenge: str | None,
        code_challenge_method: str | None,
        code_verifier: str | None,
    ) -> None:

        if not code_challenge:
            return

        if not code_verifier:
            raise InvalidGrant()

        if code_challenge_method == "S256":
            digest = hashlib.sha256(code_verifier.encode()).digest()
            computed = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
        else:
            computed = code_verifier

        if not secrets.compare_digest(computed, code_challenge):
            raise InvalidGrant()
    def _build_redirect_uri(
        self,
        redirect_uri: str,
        *,
        state: str | None,
        code: str | None = None,
        error: str | None = None,
    ) -> str:

        parts = urlsplit(redirect_uri)
        params = {"code" if code else "error": code or error or ""}
        if state is not None:
            params["state"] = state

        query = urlencode(params)

        return urlunsplit(parts._replace(query=query))

    def _validate_scopes(
        self,
        requested: list[str],
        allowed: list[str],
    ) -> None:
       
        invalid = set(requested) - set(allowed)

        if invalid:
            raise InvalidScope(
                scopes=sorted(invalid)
            )