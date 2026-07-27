from ulid import ULID

class IdGenerator:

    @staticmethod
    def session_id() -> str:
        return str(ULID())

    @staticmethod
    def request_id() -> str:
        return str(ULID())