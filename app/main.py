import uvicorn
from fastapi import FastAPI
from app.core.lifespan import lifespan
from app.modules.auth.router import router as auth_router
from app.shared.exception_handler import register_handler

app = FastAPI(lifespan=lifespan)

register_handler(app)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

def run() -> None:
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, log_config=None)