from pydantic import BaseModel, HttpUrl
from datetime import datetime
from app.shared.common import MongoDocument

class OAuthClient(MongoDocument):
    client_id: str
    client_secret_hash: str
    name: str
    redirect_urls: list[HttpUrl]
    allowed_scopes: list[str]
    grant_types: list[str]
    response_types: list[str]
    is_confidential: bool

class AuthorizationCode(BaseModel):
    code: str
    client_id: str
    user_id: str
    redirect_uri: str
    scopes: list[str]
    code_challenge: str | None = None
    code_challenge_method: str | None = None
    expires_at: datetime
    created_at: datetime