import jwt
import uuid
from datetime import datetime, timedelta, timezone
from app.config.settings import get_settings
from app.database.redis import RedisService
from app.modules.auth.schemas import AccessTokenPayload, SessionData
from app.modules.auth.exceptions import AccessTokenExpired, InvalidAccessToken, InvalidRefreshToken
from jwt import ExpiredSignatureError, InvalidTokenError
import json
import hashlib
import hmac
import secrets

settings = get_settings()

class TokenService:
    def __init__(self, redis: RedisService):

        self.secret = settings.jwt.secret

        self.refresh_secret = settings.jwt.refresh_secret
        
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

    def _refresh_key(self, refresh_token: str) -> str:
        return f"refresh:{self.hash_refresh_token(refresh_token)}"

    def _build_session(self, user_id: str, device: str, user_agent: str, ip_address: str) -> str:
        now = datetime.now(timezone.utc).isoformat()
        return SessionData(
            user_id=user_id,
            device=device,
            user_agent=user_agent,
            created_at=now,
            last_used_at=now,
            ip_address=ip_address
        ).model_dump_json()

    def create_refresh_token(self, user_id: str, device: str, user_agent: str, ip_address: str) -> str:

        session_id = secrets.token_urlsafe(64)

        session = self._build_session(user_id, device, user_agent, ip_address)

        self.redis.set(key=self._refresh_key(session_id), value=session, ttl=settings.jwt.refresh_token_expiry)

        return session_id

    def rotate_refresh_token(self, old_token: str, user_id: str, device: str, user_agent: str, ip_address: str) -> str:
        # Atomic rotate: revoke old + store new in one pipeline so a crash can't
        # leave both live or both dead. Caller holds a lock to serialize reuse.
        new_session_id = secrets.token_urlsafe(64)
        session = self._build_session(user_id, device, user_agent, ip_address)

        pipe = self.redis.pipeline()
        pipe.delete(self._refresh_key(old_token))
        pipe.set(self._refresh_key(new_session_id), session, ex=settings.jwt.refresh_token_expiry)
        pipe.execute()

        return new_session_id

    def lock(self, refresh_token: str):
        return self.redis.lock(self.hash_refresh_token(refresh_token))

    def verify_refresh_token(self, refresh_token: str) -> SessionData:

        token = self.redis.get(self._refresh_key(refresh_token))

        if not token:
            raise InvalidRefreshToken()
        else:
            return SessionData.model_validate(json.loads(token))

    def revoke_refresh_token(self, refresh_token: str):
        self.redis.delete(self._refresh_key(refresh_token))

    def hash_refresh_token(self, refresh_token: str) -> str:

        return hmac.new(
            key=self.refresh_secret.encode(),
            msg=refresh_token.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()


        


