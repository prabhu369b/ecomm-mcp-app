from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.database.dependency import get_mongo, get_redis
from app.database.mongo import MongoService
from app.database.redis import RedisService
from app.modules.auth.dependency import get_auth_service
from app.modules.auth.password import PasswordService
from app.modules.auth.oauth.client_repository import OAuthRepository
from app.modules.auth.oauth.oauth_service import OAuthService
from app.modules.auth.oauth.authorization_code.repository import AuthorizationCodeRepository
from app.modules.auth.oauth.request_repository.repository import AuthorizationRequestRepository
from app.modules.auth.service import AuthService
from app.modules.auth.token_service import TokenService
from app.modules.user.models import User

def get_oauth_service(
    mongo: MongoService = Depends(get_mongo),
    redis: RedisService = Depends(get_redis)
):
    client_repo = OAuthRepository(mongo)
    authorization_code_repo = AuthorizationCodeRepository(redis)
    request_repo = AuthorizationRequestRepository(redis)
    password_service = PasswordService()
    token_service = TokenService()

    return OAuthService(
        client_repo=client_repo,
        authorization_code_repo=authorization_code_repo,
        request_repo=request_repo,
        password_service=password_service,
        token_service=token_service,
    )