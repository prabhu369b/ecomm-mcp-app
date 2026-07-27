
class OAuthCodeKeys:
    @staticmethod
    def oauth_code(code: str) -> str:
        return f'oauth_code:{code}'