from app.database.redis import RedisService
from app.modules.product.cache_keys import ProductCacheKeys
from app.modules.product.repository import ProductRepository
from app.modules.product.schemas import ProductListResponse, ProductResponse
from app.core.logger import Logger

logger = Logger.get_logger(__name__)

LIST_CACHE_TTL = 60

class ProductService:
    def __init__(self, repo: ProductRepository, redis: RedisService):
        self.repo = repo
        self.redis = redis

    async def search(
        self, 
        q: str | None,
        category_id: str | None,
        page: int,
        page_size: int
    ) -> ProductListResponse:
        
        version = await self.redis.get(ProductCacheKeys.version_key()) or "0"
        key = ProductCacheKeys.list_key(str(version), q, category_id, page, page_size)

        cached = await self.redis.get(key)

        if cached:
            return ProductListResponse.model_validate_json(cached)

        products, total = self.repo.search(q, category_id, page, page_size)

        response = ProductListResponse(
            items=[ProductResponse(**p.model_dump()) for p in products],
            total = total,
            page = page,
            page_size = page_size
        )

        await self.redis.set(key, response.model_dump_json(), LIST_CACHE_TTL)
        return response
 # type: ignore
        