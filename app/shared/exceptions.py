from fastapi import status

class AppException(Exception):

    status_code = status.HTTP_400_BAD_REQUEST
    message = "Unknown Error"

    def __init__(self, message=None):
        if message:
            self.message = message