from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.shared.exceptions import AppException
from app.shared.response import ApiResponse
from app.core.logger import Logger

logger = Logger.get_logger(__name__)

def register_handler(app: FastAPI):

    @app.exception_handler(AppException)
    async def app_exception_handler(request, exc: AppException):

        if exc.status_code >= 500:
            logger.error(
                "unhandled app exception: path=%s status=%s message=%s",
                request.url.path, exc.status_code, exc.message,
                exc_info=exc,
            )
        else:
            logger.warning(
                "app exception: path=%s status=%s message=%s",
                request.url.path, exc.status_code, exc.message,
            )

        return JSONResponse(
            status_code=exc.status_code,
            content=ApiResponse(
                success= False,
                message=exc.message,
                data= None
            ).model_dump()
        )
