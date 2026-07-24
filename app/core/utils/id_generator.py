from ulid import ULID

class IdGenerator:

    @staticmethod
    def session_id() -> str:
        return str(ULID())