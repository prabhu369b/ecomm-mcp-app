from fastapi import APIRouter, Depends, Query
from app.modules.product.dependency import get_product_service
from app.modules.product.schemas import ProductListResponse
from app.modules.product.service import ProductService
from app.shared.response import ApiResponse

router = APIRouter()

@router.get(
    "",
    response_model=ApiResponse[ProductListResponse]
)
async def list_prodcuts(
    q: str | None = Query(default=None),
    category_id: str | None = Query(default=None),
    page: int = Query(default=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: ProductService = Depends(get_product_service)
):
    data = await service.search(q, category_id, page, page_size)
    return ApiResponse(
        success=True,
        message="Products Fetched",
        data=data
    )

