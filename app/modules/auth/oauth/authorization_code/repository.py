from app.database.redis import RedisService
from app.modules.auth.oauth.authorization_code.keys import OAuthCodeKeys
from app.modules.auth.oauth.models import AuthorizationCode
from app.core.logger import Logger

logger = Logger.get_logger(__name__)

class AuthorizationCodeRepository:
    def __init__(self, redis: RedisService) -> None:
        self.redis = redis

    async def create(self, code: AuthorizationCode):
       await self.redis.set(key=OAuthCodeKeys.oauth_code(code.code), value=code.model_dump_json(), ttl=300)
       logger.info("authorization code stored: client_id=%s user_id=%s", code.client_id, code.user_id)

    async def find(
        self,
        code: str,
    ) -> AuthorizationCode | None:

        result = await self.redis.get(OAuthCodeKeys.oauth_code(code))

        if not result:
            return None

        return AuthorizationCode.model_validate_json(
            result
        )

    async def delete(
            self,
            code: str
    ):
        await self.redis.delete(OAuthCodeKeys.oauth_code(code))
        logger.info("authorization code consumed: code_prefix=%s", code[:8])
    