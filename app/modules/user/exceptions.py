from fastapi import status
from app.shared.exceptions import AppException

class UserDisabled(AppException):
    status_code = status.HTTP_403_FORBIDDEN

    message = "User is Disabled"
