from fastapi import APIRouter, Depends, Query

from app.modules.product_v2.dependency import get_product_v2_service
from app.modules.product_v2.schemas import ProductV2ListResponse
from app.modules.product_v2.service import ProductV2Service
from app.shared.response import ApiResponse

router = APIRouter()


@router.get("", response_model=ApiResponse[ProductV2ListResponse])
async def list_products_v2(
    q: str | None = Query(default=None),
    category_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: ProductV2Service = Depends(get_product_v2_service),
):
    data = await service.search(q, category_id, page, page_size)
    return ApiResponse(success=True, message="Products Fetched", data=data)
