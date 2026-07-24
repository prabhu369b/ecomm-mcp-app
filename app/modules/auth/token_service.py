import jwt
import uuid
from datetime import datetime, timedelta, timezone
from app.config.settings import get_settings
from app.database.redis import RedisService
from app.modules.auth.schemas import AccessTokenPayload, SessionData
from app.modules.auth.exceptions import AccessTokenExpired, InvalidAccessToken
from jwt import ExpiredSignatureError, InvalidTokenError
import json

settings = get_settings()

class TokenService:
    def __init__(self, redis: RedisService):

        self.secret = settings.jwt.secret
        
        self.algorithm = settings.jwt.algorithm

        self.redis = redis

    def create_access_token(self, user_id: str):

        now = datetime.now(timezone.utc)

        expires = now + timedelta(
            seconds=settings.jwt.access_token_expiry
        )

        payload = {
            "sub": user_id,
            "iat": now,
            "exp": expires,
            "iss": settings.jwt.issuer,
            "aud": settings.jwt.audience,
            "jti": str(uuid.uuid4()) 
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
            raise AccessTokenExpired()
    
        except InvalidTokenError:
            raise InvalidAccessToken()

    def create_refresh_token(self, user_id: str, device: str, user_agent: str, ip_address: str) -> str:

        session_id = str(uuid.uuid4())
        key = f"refresh:{user_id}:{session_id}"
        session = SessionData(
            user_id= user_id,
            device=device,
            user_agent=user_agent,
            created_at=datetime.now(timezone.utc).isoformat(),
            last_used_at=datetime.now(timezone.utc).isoformat(),
            ip_address=ip_address
        ).model_dump_json()

        self.redis.set(key=key, value=session, ttl=settings.jwt.refresh_token_expiry)

        return session_id
