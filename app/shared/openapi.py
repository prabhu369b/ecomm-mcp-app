from app.shared.response import ApiResponse
from app.shared.exceptions import AppException


def error_responses(*exceptions: type[AppException]) -> dict:
    """Build OpenAPI `responses` from AppException classes.
    Same status_code groups together, each keeps its own message."""
    grouped: dict[int, list[type[AppException]]] = {}
    for exc in exceptions:
        grouped.setdefault(exc.status_code, []).append(exc)

    return {
        code: {
            "model": ApiResponse[None],
            "content": {
                "application/json": {
                    "examples": {
                        exc.__name__: {
                            "summary": exc.message,
                            "value": {"success": False, "message": exc.message, "data": None},
                        }
                        for exc in excs
                    }
                }
            },
        }
        for code, excs in grouped.items()
    }
