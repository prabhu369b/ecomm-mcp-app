from app.modules.auth.schemas import RegisterRequest, UserResponse
from app.modules.user.repository import UserRepository
from app.modules.auth.password import PasswordService
from app.modules.user.models import User
from app.modules.auth.exceptions import UsernameAlreadyExists, EmailAlreadyExists

class AuthService:

    def __init__(self, user_repo: UserRepository, password_service: PasswordService):
        self.user_repo = user_repo
        self.password = password_service
    
    def register(self, request: RegisterRequest):
        
        if self.user_repo.exists_email(request.email):
            raise EmailAlreadyExists()
        if self.user_repo.exists_username(request.username):
            raise UsernameAlreadyExists()
        
        hashed = self.password.hash(password=request.password)
        
        user = User(
            name=request.name,
            username=request.username,
            email=request.email,
            password_hash = hashed
        )

        user = self.user_repo.create(user)
    
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            username=user.username
        )
