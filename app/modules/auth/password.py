from argon2 import PasswordHasher


class PasswordService:
    def __init__(self):
        self.hasher = PasswordHasher()

    def hash(self, password: str) -> str:
        return self.hasher.hash(password)

    def verify(self, hash: str, password: str):
        return self.hasher.verify(hash, password)
