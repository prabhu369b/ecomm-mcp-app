from fastapi import status

from app.shared.exceptions import AppException


class OAuthClientNotFound(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "OAuth client not found."


class InvalidRedirectUri(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Invalid redirect URI."


class AuthorizationRequestNotFound(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Authorization request not found or expired."


class InvalidGrant(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Invalid, expired, or already used authorization code."


class InvalidClient(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Client authentication failed."


class InvalidScope(AppException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, scopes: list[str]):
        self.message = (
            f"Invalid scope(s): {', '.join(scopes)}"
        )