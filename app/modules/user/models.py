from app.shared.common import MongoDocument
from pydantic import BaseModel, EmailStr, Field

class User(MongoDocument):
    name: str
    username: str
    email: EmailStr
    password_hash: str

    roles: list[str] = Field(default_factory=lambda: ["user"])
    scopes: list[str] = Field(default_factory=lambda: ["product:read"])

    is_active: bool = True

    # TODO Need to add Email Verification
    # is_verified: bool = False