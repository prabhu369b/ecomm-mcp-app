from .common import MongoDocument
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class User(MongoDocument):
    name: str
    email: EmailStr
    password_hash: str