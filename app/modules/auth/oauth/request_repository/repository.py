

from app.database.redis import RedisService
from app.modules.auth.oauth.schemas import AuthorizationRequest
from app.modules.auth.oauth.request_repository.keys import AuthorizationRequestKeys


class AuthorizationRequestRepository:

    def __init__(self, redis: RedisService) -> None:
        self.redis = redis

    async def create(self, request_id: str, request: AuthorizationRequest):
        await self.redis.set(AuthorizationRequestKeys.authorization_request(request_id), value=request.model_dump_json(), ttl=300)

    async def find(self, request_id: str) -> AuthorizationRequest | None:
        result = await self.redis.get(AuthorizationRequestKeys.authorization_request(request_id))
        if not result:
            return None
        return AuthorizationRequest.model_validate_json(result)

    async def delete(self, request_id: str):
        await self.redis.delete(AuthorizationRequestKeys.authorization_request(request_id))