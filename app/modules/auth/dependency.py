from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.modules.user.repository import UserRepository
from app.modules.auth.password import PasswordService
from app.modules.auth.service import AuthService
from app.database.dependency import get_mongo, get_redis
from app.modules.auth.token_service import TokenService
from app.modules.auth.exceptions import InvalidAccessToken
from app.modules.user.exceptions import UserDisabled
from app.modules.auth.schemas import AuthenticatedUser


def get_auth_service(
    mongo = Depends(get_mongo),
    redis = Depends(get_redis)
    ):
    
    repo = UserRepository(mongo)
    password = PasswordService()
    token = TokenService(redis)

    return AuthService(
        user_repo=repo,
        password_service=password,
        token_service=token
    )

oauth2_schema = OAuth2PasswordBearer(
    tokenUrl="auth/sign-in"
)


def get_current_user(
  token: str = Depends(oauth2_schema),
  mongo = Depends(get_mongo),
  redis = Depends(get_redis)
):
    repo = UserRepository(mongo)
    token_service = TokenService(redis)

    payload = token_service.verify_access_token(
        token=token
    )

    user = repo.find_by_id(user_id=payload.sub)
    
    if user is None:
        raise InvalidAccessToken()
    
    if not user.is_active:
        raise UserDisabled()
    
    return AuthenticatedUser(
        user_id=str(user.id),
        name=user.name,
        username=user.username,
        email=user.email,
        roles=user.roles,
        scops=user.scopes
    )