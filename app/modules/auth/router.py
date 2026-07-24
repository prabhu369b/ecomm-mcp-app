from fastapi import APIRouter, Depends, status, Request
from app.modules.auth.schemas import RegisterRequest, UserResponse, AuthenticatedUser,  LoginRequest, LoginResponse, LoginContext, RefreshTokenRequest
from app.modules.auth.service import AuthService
from app.modules.auth.dependency import get_auth_service, get_current_user
from app.modules.auth.exceptions import UsernameAlreadyExists, EmailAlreadyExists, InvalidAccessToken, AccessTokenExpired
from app.modules.user.exceptions import UserDisabled
from app.shared.response import ApiResponse
from app.shared.openapi import error_responses

router = APIRouter()

@router.post(
        "/sign-up",
        response_model=ApiResponse[UserResponse],
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(UsernameAlreadyExists, EmailAlreadyExists),
)
async def register(request: RegisterRequest, service: AuthService = Depends(get_auth_service)):
    user = service.register(request)

    return ApiResponse(
        success=True,
        message="User Registered Successfully",
        data=user
    )

@router.post(
    "/sign-in",
    response_model=ApiResponse[LoginResponse],
)
async def login(
    request: Request,
    body: LoginRequest,
    service: AuthService = Depends(get_auth_service)
):
    context = LoginContext(
        device=body.device,
        ip_address=request.client.host,
        user_agent=request.headers.get("User-Agent", ""),
    )

    response = service.login(body, context)
    

    return ApiResponse(
        success=True,
        message="Login successful",
        data=response
    )

@router.get(
    "/me",
    response_model=ApiResponse[AuthenticatedUser],
    status_code=status.HTTP_200_OK,
    responses=error_responses(InvalidAccessToken, AccessTokenExpired, UserDisabled) 
)
async def me(current_user: AuthenticatedUser = Depends(get_current_user)):
    return ApiResponse(
        success=True,
        message="Profile Fetched",
        data=current_user
    )

@router.post("/refresh",
             response_model=LoginResponse,
             status_code=status.HTTP_200_OK
)
async def refresh(request: RefreshTokenRequest, service: AuthService = Depends(get_auth_service)):
    response = service.refresh(
        request.refresh_token
    )

    return ApiResponse(
        success=True,
        message="Token Refreshed Successfully",
        data=response
    )