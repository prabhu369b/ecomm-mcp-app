from fastapi import APIRouter, Depends

from app.modules.auth.dependency import get_current_user
from app.modules.order.dependency import get_order_service
from app.modules.order.schemas import OrderListResponse, OrderResponse
from app.shared.response import ApiResponse


router = APIRouter()

@router.post("/checkout", response_model=ApiResponse[OrderResponse])
async def checkout(user=Depends(get_current_user), service=Depends(get_order_service)):
    return ApiResponse(success=True, message="Order placed", data=await service.checkout(user.user_id))

@router.get("", response_model=ApiResponse[OrderListResponse])
async def list_orders(page: int = 1, page_size: int = 20, user=Depends(get_current_user), service=Depends(get_order_service)):
    return ApiResponse(success=True, message="Orders fetched", data=await service.list(user.user_id, page, page_size))

@router.get("/{order_id}", response_model=ApiResponse[OrderResponse])
async def get_order(order_id: str, user=Depends(get_current_user), service=Depends(get_order_service)):
    return ApiResponse(success=True, message="Order fetched", data=await service.get(user.user_id, order_id))