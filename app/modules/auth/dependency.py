from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.modules.user.repository import UserRepository
from app.modules.auth.password import PasswordService
from app.modules.auth.service import AuthService
from app.database.dependency import get_mongo, get_redis
from app.modules.auth.token_service import TokenService
from app.modules.auth.exceptions import AccessTokenExpired, InvalidAccessToken
from app.modules.user.exceptions import UserDisabled
from app.modules.auth.schemas import AuthenticatedUser
from app.modules.auth.session.repository import SessionRepository
from app.database.mongo import MongoService
from app.database.redis import RedisService
from app.database.lock import RedisLockService


def get_auth_service(
    mongo: MongoService = Depends(get_mongo),
    redis: RedisService = Depends(get_redis)
    ):

    user_repo = UserRepository(mongo)
    password = PasswordService()
    token = TokenService()
    session_repo = SessionRepository(redis)
    lock_service = RedisLockService(redis)

    return AuthService(
        user_repo=user_repo,
        session_repo=session_repo,
        password_service=password,
        token_service=token,
        lock_service=lock_service
    )

oauth2_schema = OAuth2PasswordBearer(
    tokenUrl="auth/sign-in"
)


def get_current_user(
  token: str = Depends(oauth2_schema),
  mongo = Depends(get_mongo),
):
    repo = UserRepository(mongo)
    token_service = TokenService()

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

optional_oauth2_schema = OAuth2PasswordBearer(
    tokenUrl="auth/sign-in",
    auto_error=False
)

def get_optional_current_user(
  token: str | None = Depends(optional_oauth2_schema),
  mongo = Depends(get_mongo),
):
    if not token:
        return None
    try:
        repo = UserRepository(mongo)
        token_service = TokenService()

        payload = token_service.verify_access_token(
            token=token
        )

        user = repo.find_by_id(user_id=payload.sub)
        
        if user is None:
            return None
        
        if not user.is_active:
            return None
        
        return AuthenticatedUser(
                user_id=str(user.id),
                name=user.name,
                username=user.username,
                email=user.email,
                roles=user.roles,
                scops=user.scopes
        )
    except InvalidAccessToken or AccessTokenExpired:
            return None