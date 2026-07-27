from fastapi import status
from app.shared.exceptions import AppException


class EmptyCart(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Cart is empty"


class OrderNotFound(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Order not found"