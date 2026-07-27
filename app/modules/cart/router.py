from fastapi import APIRouter, Depends

from app.modules.auth.dependency import get_current_user
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.cart.dependency import get_cart_service
from app.modules.cart.schemas import CartItemRequest, CartResponse
from app.modules.cart.service import CartService
from app.shared.response import ApiResponse


router = APIRouter()

@router.get("", response_model=ApiResponse[CartResponse])
async def get_cart(
    user: AuthenticatedUser = Depends(get_current_user),
    service: CartService = Depends(get_cart_service)
):
    return ApiResponse(
        success=True,
        message="Cart fetched",
        data= await service.get(user.user_id)
    )

@router.post("/items", response_model=ApiResponse[CartResponse])
async def add_item(
    body: CartItemRequest,
    user: AuthenticatedUser = Depends(get_current_user),
    service: CartService = Depends(get_cart_service)
):
    data = await service.add_item(user.user_id, body.product_id, body.qty)
    return ApiResponse(success=True, message="Item added", data=data)

@router.patch("items/{product_id}", response_model=ApiResponse[CartResponse])
async def update_item(
    product_id: str, 
    body: CartItemRequest,
    user: AuthenticatedUser = Depends(get_current_user),
    service: CartService = Depends(get_cart_service)
):
    data = await service.update_item(user.user_id, product_id, body.qty)
    return ApiResponse(success=True, message="Item updated", data=data)

@router.delete("items/{product_id}", response_model=ApiResponse[CartResponse])
async def remove_cart_item(
    product_id: str, 
    user: AuthenticatedUser = Depends(get_current_user),
    service: CartService = Depends(get_cart_service)
):
    data = await service.remove_item(user.user_id, product_id)
    return ApiResponse(success=True, message="Item removed", data=data)

@router.delete("", status_code=204)
async def clear_cart(
    user: AuthenticatedUser = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
):
    await service.clear(user.user_id)