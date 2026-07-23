from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.shared.exceptions import AppException
from app.shared.response import ApiResponse

def register_handler(app: FastAPI):

    @app.exception_handler(AppException)
    async def app_exception_handler(request, exc: AppException):

        return JSONResponse(
            status_code=exc.status_code,
            content=ApiResponse(
                success= False,
                message=exc.message,
                data= None
            ).model_dump()
        )
