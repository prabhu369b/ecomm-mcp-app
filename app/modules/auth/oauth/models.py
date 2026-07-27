from datetime import datetime
from pydantic import HttpUrl
from shared.common import MongoDocument

class OAuthClient(MongoDocument):
    client_id: str
    client_secret_hash: str
    name: str
    redirect_urls: list[HttpUrl]
    allowed_scopes: list[str]
    grant_types: list[str]
    response_types: list[str]
    is_confidential: bool