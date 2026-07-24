from fastapi import status
from app.shared.exceptions import AppException

class UsernameAlreadyExists(AppException):
    
    status_code = status.HTTP_409_CONFLICT
    message = "Username already exists"

class EmailAlreadyExists(AppException):
    
    status_code = status.HTTP_409_CONFLICT
    message = "Email already exists"

class InvalidCredentials(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid email or password"


class UserDisabled(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    message = "User account is disabled"


class EmailNotVerified(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    message = "Email address is not verified"

class InvalidAccessToken(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid Access Token"

class AccessTokenExpired(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Access token expired" 

class InvalidRefreshToken(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid Refresh Token"