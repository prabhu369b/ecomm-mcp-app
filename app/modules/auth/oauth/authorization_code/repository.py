from app.database.redis import RedisService
from app.modules.auth.oauth.authorization_code.keys import OAuthCodeKeys
from app.modules.auth.oauth.models import AuthorizationCode

class AuthorizationCodeRepository:
    def __init__(self, redis: RedisService) -> None:
        self.redis = redis

    async def create(self, code: AuthorizationCode):
       await self.redis.set(key=OAuthCodeKeys.oauth_code(code.code), value=code.model_dump_json(), ttl=300)

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
    