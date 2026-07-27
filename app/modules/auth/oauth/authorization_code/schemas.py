
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, HttpUrl

from app.modules.auth.oauth.models import OAuthClient


class AuthorizationResult(BaseModel):
    requires_login: bool
    requires_consent: bool
    client: OAuthClient

class CreateAuthCode(BaseModel):
    client_id: str
    user_id: str
    redirect_uri: list[HttpUrl]
    scopes: list[str]
    expires_at: datetime


