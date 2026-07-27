from bson import ObjectId
from app.modules.user.models import User
from app.database.mongo import MongoService
from pydantic import EmailStr

class UserRepository:

    def __init__(self, mongo: MongoService):
        self.collection = mongo.db.users
    def exists_username(self, username: str) -> bool:
        return self.collection.find_one({"username": username}) is not None
    
    def exists_email(self, email: EmailStr) -> bool:
        return self.collection.find_one({"email":email}) is not None

    def create(self, user: User):
        document = user.model_dump(exclude={"id"})
        result = self.collection.insert_one(document)
        user.id = str(result.inserted_id)
        return user
    
    def find_by_id(self, user_id: str) -> User | None:
        document = self._to_user(self.collection.find_one({"_id": ObjectId(user_id)}))
        if document is None:
            return None

        return User.model_validate(document)

    def find_by_email(self, email: EmailStr) -> User | None:
        document = self._to_user(self.collection.find_one({"email": email}))
        if document is None:
            return None

        return User.model_validate(document)

    @staticmethod
    def _to_user(doc: dict | None) -> User | None:
        if doc is None:
            return None
        doc["id"] = str(doc.pop("_id"))
        return User(**doc)