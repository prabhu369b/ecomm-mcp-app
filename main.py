from fastapi import FastAPI
from config.settings import get_settings
from core.lifespan import lifespan
import uvicorn

app = FastAPI(lifespan=lifespan)

    