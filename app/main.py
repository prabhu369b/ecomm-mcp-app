from contextlib import AsyncExitStack, asynccontextmanager

import uvicorn
from fastapi import APIRouter, FastAPI
from app.core.lifespan import lifespan
from app.modules.auth.router import router as auth_router
from app.modules.auth.oauth.router import router as oauth_router
from app.modules.auth.oauth.well_known_router import router as well_known_router
from app.modules.mcp.server import mcp_server
from app.shared.exception_handler import register_handler

mcp_app = mcp_server.streamable_http_app()

@asynccontextmanager
async def combined_lifespan(app: FastAPI):
    async with AsyncExitStack() as stack:
        await stack.enter_async_context(lifespan(app))
        await stack.enter_async_context(mcp_app.router.lifespan_context(app))
        yield

app = FastAPI(lifespan=combined_lifespan)

register_handler(app)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(oauth_router, prefix="/oauth", tags=["OAuth"])
app.include_router(well_known_router, tags=["OAuth Discovery"])

frontend_router = APIRouter()
frontend_router.frontend("/", directory="web/dist", fallback="index.html")
app.include_router(frontend_router, prefix="/app")

# Mounted at "/mcp", not "/": a root Mount matches Match.FULL for every
# path unconditionally, so it wins ahead of any route (including the SPA
# frontend fallback below) no matter what order it's registered in.
app.mount("/mcp", mcp_app)

def run() -> None:
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, log_config=None)