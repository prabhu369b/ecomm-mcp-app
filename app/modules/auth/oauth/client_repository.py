from app.database.mongo import MongoService
from app.modules.auth.oauth.models import OAuthClient

class OAuthRepository:

    def __init__(self, mongo: MongoService):
        self.collection = mongo.db.oauth_clients

    async def create(self, client: OAuthClient):
        document = client.model_dump(exclude={"id"}, mode='json')
        result = self.collection.insert_one(document)
        return result.inserted_id

    async def find_client_by_id(self, client_id: str) -> OAuthClient | None:
        document = self._to_client(self.collection.find_one({'client_id': client_id}))
        if document is None:
            return None
        return OAuthClient.model_validate(document)

    @staticmethod
    def _to_client(doc: dict | None) -> OAuthClient | None:
        if doc is None:
            return None
        doc["id"] = str(doc.pop("_id"))
        return OAuthClient(**doc)



