from app.modules.auth.schemas import RegisterRequest, UserResponse, LoginRequest, LoginResponse, LoginContext
from app.modules.user.repository import UserRepository
from app.modules.auth.password import PasswordService
from app.modules.user.models import User
from app.modules.auth.exceptions import UsernameAlreadyExists, EmailAlreadyExists, InvalidCredentials, UserDisabled, InvalidRefreshToken
from app.modules.auth.token_service import TokenService
from app.config.settings import get_settings

settings = get_settings()
class AuthService:

    def __init__(self, user_repo: UserRepository, password_service: PasswordService, token_service: TokenService):
        self.user_repo = user_repo
        self.password = password_service
        self.token_service = token_service
    
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
    
    def login(self, body:LoginRequest, context: LoginContext):

        user = self.user_repo.find_by_email(body.email)
        if not user:
            raise InvalidCredentials()
         
        valid = self.password.verify(hash=user.password_hash, password=body.password,)

        if not valid:
            raise InvalidCredentials()
        
        if not user.is_active:
            raise UserDisabled()
        
        # TODO Need to add Email Verification
        # if not user.is_verified:
        #     raise EmailNotVerified()
        
        
        
        token = self.token_service.create_access_token(str(user.id))
        
        refresh_token = self.token_service.create_refresh_token(
            user_id=str(user.id), 
            device=context.device,
            ip_address=context.ip_address,
            user_agent=context.user_agent
        )
        

        return LoginResponse(
            access_token=token,
            refresh_token=refresh_token,
            expires_in=settings.jwt.access_token_expiry
        )

    def refresh(self, refresh_token: str) -> LoginResponse:

        with self.token_service.lock(refresh_token):

            session = self.token_service.verify_refresh_token(refresh_token)

            user = self.user_repo.find_by_id(session.user_id)

            if not user:
                raise InvalidRefreshToken()

            if not user.is_active:
                raise UserDisabled()

            access = self.token_service.create_access_token(str(user.id))

            refresh = self.token_service.rotate_refresh_token(
                old_token=refresh_token,
                user_id=str(user.id),
                device=session.device,
                ip_address=session.ip_address,
                user_agent=session.user_agent,
            )

        return LoginResponse(
            access_token=access,
            refresh_token=refresh,
            expires_in=settings.jwt.access_token_expiry
        )