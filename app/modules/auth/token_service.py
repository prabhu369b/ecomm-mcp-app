import jwt
import uuid
from datetime import datetime, timedelta, timezone
from app.config.settings import get_settings
from app.modules.auth.schemas import AccessTokenPayload
from app.modules.auth.exceptions import AccessTokenExpired, InvalidAccessToken
from jwt import ExpiredSignatureError, InvalidTokenError
import hashlib
import hmac
import secrets
from app.core.logger import Logger

settings = get_settings()
logger = Logger.get_logger(__name__)

class TokenService:
    def __init__(self):

        self.secret = settings.jwt.secret

        self.refresh_secret = settings.jwt.refresh_secret

        self.algorithm = settings.jwt.algorithm

    def create_access_token(
        self,
        user_id: str,
        session_id: str,
        *,
        scope: str | None = None,
        client_id: str | None = None,
    ):

        now = datetime.now(timezone.utc)

        expires = now + timedelta(
            seconds=settings.jwt.access_token_expiry
        )

        payload = {
            "sub": user_id,
            "sid": session_id,
            "iat": now,
            "exp": expires,
            "iss": settings.jwt.issuer,
            "aud": settings.jwt.audience,
            "jti": str(uuid.uuid4()),
            "scope": scope,
            "client_id": client_id,
        }

        return jwt.encode(
            payload,
            self.secret,
            algorithm=self.algorithm
        )

    def verify_access_token(self, token: str) -> AccessTokenPayload:

        try:

            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                issuer=settings.jwt.issuer,
                audience=settings.jwt.audience
            )

            return AccessTokenPayload.model_validate(
                payload
            )

        except ExpiredSignatureError:
            logger.info("access token verification failed: expired")
            raise AccessTokenExpired()

        except InvalidTokenError:
            logger.warning("access token verification failed: invalid token")
            raise InvalidAccessToken()

    @staticmethod
    def generate_refresh_token() -> str:
        return secrets.token_urlsafe(64)

    def hash_refresh_token(self, refresh_token: str) -> str:

        return hmac.new(
            key=self.refresh_secret.encode(),
            msg=refresh_token.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
