from fastapi import APIRouter, Depends, status
from app.modules.auth.schemas import RegisterRequest, UserResponse
from app.modules.auth.service import AuthService
from app.modules.auth.dependency import get_auth_service
from app.modules.auth.exceptions import UsernameAlreadyExists, EmailAlreadyExists
from app.shared.response import ApiResponse
from app.shared.openapi import error_responses

router = APIRouter()

@router.post(
        "/sign-up",
        response_model=ApiResponse[UserResponse],
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(UsernameAlreadyExists, EmailAlreadyExists),
)
def register(request: RegisterRequest, service: AuthService = Depends(get_auth_service)):
    user = service.register(request)

    return ApiResponse(
        success=True,
        message="User Registered Successfully",
        data=user
    )
