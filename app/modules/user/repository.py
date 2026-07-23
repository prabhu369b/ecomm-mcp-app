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
        # timestamps to bottom (pydantic puts base-class fields first)
        for key in ("created_at", "updated_at"):
            document[key] = document.pop(key)
        result = self.collection.insert_one(document)
        user.id = str(result.inserted_id)
        return user