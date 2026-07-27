class AuthorizationRequestKeys:
    @staticmethod
    def authorization_request(request_id: str) -> str:
        return f"oauth:request:{request_id}"
