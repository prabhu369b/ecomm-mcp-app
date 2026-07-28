from app.database.redis import RedisService
from app.modules.product_v2.cache_keys import ProductV2CacheKeys
from app.modules.product_v2.repository import ProductV2Repository
from app.modules.product_v2.schemas import ProductV2ListResponse, ProductV2Response
from app.core.logger import Logger

logger = Logger.get_logger(__name__)

LIST_CACHE_TTL = 60


class ProductV2Service:
    def __init__(self, repo: ProductV2Repository, redis: RedisService):
        self.repo = repo
        self.redis = redis

    async def search(
        self,
        q: str | None,
        category_id: str | None,
        page: int,
        page_size: int,
    ) -> ProductV2ListResponse:
        version = await self.redis.get(ProductV2CacheKeys.version_key()) or "0"
        key = ProductV2CacheKeys.list_key(str(version), q, category_id, page, page_size)

        cached = await self.redis.get(key)
        if cached:
            return ProductV2ListResponse.model_validate_json(cached)

        products, total = self.repo.search(q, category_id, page, page_size)

        response = ProductV2ListResponse(
            items=[ProductV2Response(**p.model_dump()) for p in products],
            total=total,
            page=page,
            page_size=page_size,
        )

        await self.redis.set(key, response.model_dump_json(), LIST_CACHE_TTL)
        logger.info("product_v2 search: q=%s category_id=%s page=%s total=%s", q, category_id, page, total)
        return response
