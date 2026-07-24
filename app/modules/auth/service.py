from app.modules.auth.schemas import RegisterRequest, UserResponse, LoginRequest, LoginResponse, LoginContext, SessionData
from app.modules.user.repository import UserRepository
from app.modules.auth.password import PasswordService
from app.modules.user.models import User
from app.modules.auth.exceptions import UsernameAlreadyExists, EmailAlreadyExists, InvalidCredentials, UserDisabled, InvalidRefreshToken
from app.modules.auth.token_service import TokenService
from app.config.settings import get_settings
from app.modules.auth.session.repository import SessionRepository
from app.core.utils.id_generator import IdGenerator
from app.database.lock import RedisLockService
from app.modules.auth.session.keys import SessionKeys
from datetime import datetime, timezone

settings = get_settings()
class AuthService:

    def __init__(self, user_repo: UserRepository, session_repo: SessionRepository, password_service: PasswordService, token_service: TokenService, lock_service: RedisLockService):
        self.user_repo = user_repo
        self.password = password_service
        self.token_service = token_service
        self.session_repo = session_repo
        self.lock_service = lock_service
    
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
        
        
        session_id = IdGenerator.session_id()
        
        token = self.token_service.create_access_token(user_id=str(user.id), session_id=session_id)
        
        refresh_token = self.token_service.generate_refresh_token()

        refresh_hash = self.token_service.hash_refresh_token(
            refresh_token
        )

        now = datetime.now(timezone.utc).isoformat()

        session = SessionData(
            session_id=session_id,
            user_id=str(user.id),
            refresh_hash=refresh_hash,
            device=context.device,
            ip_address=context.ip_address,
            user_agent=context.user_agent,
            created_at=now,
            last_used_at=now,
        )
        
        self.session_repo.create(session=session)

        return LoginResponse(
            access_token=token,
            refresh_token=refresh_token,
            expires_in=settings.jwt.access_token_expiry
        )

    def refresh(self, refresh_token: str) -> LoginResponse:

        refresh_hash = self.token_service.hash_refresh_token(refresh_token)

        session = self.session_repo.find_by_refresh_hash(refresh_hash)

        if not session:
            raise InvalidRefreshToken()

        user = self.user_repo.find_by_id(session.user_id)

        if not user:
            raise InvalidRefreshToken()

        if not user.is_active:
            raise UserDisabled()

        with self.lock_service.acquire(SessionKeys.session(session.session_id)):

            new_refresh = self.token_service.generate_refresh_token()

            new_hash = self.token_service.hash_refresh_token(
                new_refresh
            )

            self.session_repo.rotate(
                session=session,
                old_hash=refresh_hash,
                new_hash=new_hash,
            )

        access = self.token_service.create_access_token(
            user_id=str(user.id),
            session_id=session.session_id,
        )

        return LoginResponse(
            access_token=access,
            refresh_token=new_refresh,
            token_type="Bearer",
            expires_in=settings.jwt.access_token_expiry
        )

    def logout(self, refresh_token: str):

        refresh_hash = self.token_service.hash_refresh_token(refresh_token)

        session = self.session_repo.find_by_refresh_hash(refresh_hash)

        if session:
            self.session_repo.revoke(session)

