from app.modules.auth.schemas import RegisterRequest, UserResponse, LoginRequest, LoginResponse, LoginContext, SessionData, UpdateProfileRequest, AuthenticatedUser
from app.modules.user.repository import UserRepository
from app.modules.auth.password import PasswordService
from app.modules.user.models import User
from app.modules.auth.exceptions import UsernameAlreadyExists, EmailAlreadyExists, InvalidCredentials, UserDisabled, InvalidRefreshToken, InvalidAccessToken
from app.modules.auth.token_service import TokenService
from app.config.settings import get_settings
from app.modules.auth.session.repository import SessionRepository
from app.core.utils.id_generator import IdGenerator
from app.database.lock import RedisLockService
from app.modules.auth.session.keys import SessionKeys
from datetime import datetime, timezone
from app.core.logger import Logger

settings = get_settings()
logger = Logger.get_logger(__name__)

class AuthService:

    def __init__(self, user_repo: UserRepository, session_repo: SessionRepository, password_service: PasswordService, token_service: TokenService, lock_service: RedisLockService):
        self.user_repo = user_repo
        self.password = password_service
        self.token_service = token_service
        self.session_repo = session_repo
        self.lock_service = lock_service
    
    def register(self, request: RegisterRequest):

        if self.user_repo.exists_email(request.email):
            logger.warning("register failed: email already exists username=%s", request.username)
            raise EmailAlreadyExists()
        if self.user_repo.exists_username(request.username):
            logger.warning("register failed: username already exists username=%s", request.username)
            raise UsernameAlreadyExists()

        hashed = self.password.hash(password=request.password)

        user = User(
            name=request.name,
            username=request.username,
            email=request.email,
            password_hash = hashed
        )


        user = self.user_repo.create(user)

        if user is None or user.id is None:
            return None
        
        logger.info("user registered: user_id=%s username=%s", user.id, user.username)

        return UserResponse(
            id=str(user.id),
            name=user.name,
            email=user.email,
            username=user.username
        )
    
    def update_profile(self, user_id: str, request: UpdateProfileRequest) -> AuthenticatedUser:
        fields = {}

        if request.username is not None:
            existing = self.user_repo.exists_username(request.username)
            current = self.user_repo.find_by_id(user_id)
            if existing and (current is None or current.username != request.username):
                logger.warning("update_profile failed: username taken user_id=%s", user_id)
                raise UsernameAlreadyExists()
            fields["username"] = request.username

        if request.name is not None:
            fields["name"] = request.name

        user = self.user_repo.update(user_id, fields) if fields else self.user_repo.find_by_id(user_id)

        if user is None:
            raise InvalidAccessToken()  # unreachable in practice: caller already resolved this user_id

        logger.info("profile updated: user_id=%s fields=%s", user_id, list(fields.keys()))

        return AuthenticatedUser(
            user_id=str(user.id),
            name=user.name,
            username=user.username,
            email=user.email,
            roles=user.roles,
            scops=user.scopes
        )

    async def login(self, body:LoginRequest, context: LoginContext):

        user = self.user_repo.find_by_email(body.email)
        if not user:
            logger.warning("login failed: unknown email ip=%s", context.ip_address)
            raise InvalidCredentials()

        valid = self.password.verify(hash=user.password_hash, password=body.password,)

        if not valid:
            logger.warning("login failed: invalid password user_id=%s ip=%s", user.id, context.ip_address)
            raise InvalidCredentials()

        if not user.is_active:
            logger.warning("login failed: user disabled user_id=%s", user.id)
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

        now = datetime.now(timezone.utc)

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
        
        await self.session_repo.create(session=session)

        logger.info("login success: user_id=%s session_id=%s ip=%s", user.id, session_id, context.ip_address)

        return LoginResponse(
            access_token=token,
            refresh_token=refresh_token,
            expires_in=settings.jwt.access_token_expiry
        )

    async def refresh(self, refresh_token: str) -> LoginResponse:

        refresh_hash = self.token_service.hash_refresh_token(refresh_token)

        session = await self.session_repo.find_by_refresh_hash(refresh_hash)

        if not session:
            logger.warning("refresh failed: unknown/expired refresh token")
            raise InvalidRefreshToken()

        user = self.user_repo.find_by_id(session.user_id)

        if not user:
            logger.warning("refresh failed: user not found user_id=%s", session.user_id)
            raise InvalidRefreshToken()

        if not user.is_active:
            logger.warning("refresh failed: user disabled user_id=%s", user.id)
            raise UserDisabled()

        async with self.lock_service.acquire(SessionKeys.session(session.session_id)):

            new_refresh = self.token_service.generate_refresh_token()

            new_hash = self.token_service.hash_refresh_token(
                new_refresh
            )

            await self.session_repo.rotate(
                session=session,
                old_hash=refresh_hash,
                new_hash=new_hash,
            )

        access = self.token_service.create_access_token(
            user_id=str(user.id),
            session_id=session.session_id,
        )

        logger.info("refresh success: user_id=%s session_id=%s", user.id, session.session_id)

        return LoginResponse(
            access_token=access,
            refresh_token=new_refresh,
            token_type="Bearer",
            expires_in=settings.jwt.access_token_expiry
        )

    async def logout(self, refresh_token: str):

        refresh_hash = self.token_service.hash_refresh_token(refresh_token)

        session = await self.session_repo.find_by_refresh_hash(refresh_hash)

        if session:
            await self.session_repo.revoke(session)
            logger.info("logout success: user_id=%s session_id=%s", session.user_id, session.session_id)
        else:
            logger.warning("logout failed: unknown/expired refresh token")

