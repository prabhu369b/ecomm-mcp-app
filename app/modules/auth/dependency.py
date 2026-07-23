from fastapi import Depends
from app.modules.user.repository import UserRepository
from app.modules.auth.password import PasswordService
from app.modules.auth.service import AuthService
from app.database.dependency import get_mongo



def get_auth_service(
    mongo = Depends(get_mongo)):
    repo = UserRepository(mongo)
    password = PasswordService()

    return AuthService(
        user_repo=repo,
        password_service=password
    )
