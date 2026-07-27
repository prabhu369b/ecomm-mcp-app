from fastapi import status
from app.shared.exceptions import AppException

class ProductNotFound(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Product not found"

class InsufficientStock(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Not enough stock"