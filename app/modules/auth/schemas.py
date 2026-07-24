from pydantic import BaseModel, EmailStr, field_validator
import re
from datetime import datetime

class RegisterRequest(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]" ,value):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain a lowercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain a number")
        if not re.search(r"[!@#$%^&*]", value):
            raise ValueError("Password must contain a special character")
        return value

class UserResponse(BaseModel):

    id: str
    name: str
    username: str
    email: EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    device: str

class LoginContext(BaseModel):
    device: str
    ip_address: str
    user_agent: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int

class LogoutRequest(BaseModel):
    refresh_token: str

class AccessTokenPayload(BaseModel):
    sub: str
    iat: datetime
    exp: datetime
    iss: str
    aud: str
    jti: str

class AuthenticatedUser(BaseModel):
    user_id: str
    name: str
    username: str
    email: EmailStr
    roles: list[str]
    scops: list[str]

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class SessionData(BaseModel):
    user_id: str
    device: str
    ip_address: str
    user_agent: str
    created_at: datetime
    last_used_at: datetime