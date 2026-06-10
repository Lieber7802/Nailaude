"""
Nailaude Backend - FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.router import api_router
from app.api.responses import api_error, validation_api_error
from app.config import settings
from app.database import Base, async_session, engine, get_db
from app.services.preview_service import PreviewService
from app.services.seed import seed_builtin_data
from app.ws.handlers import ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.AUTO_CREATE_SCHEMA:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        await seed_builtin_data(session)
    try:
        yield
    finally:
        await PreviewService.shutdown_dev_servers()


app = FastAPI(
    title="Nailaude API",
    description="IM-style Multi-Agent Collaboration Workstation",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API routes
app.include_router(api_router, prefix="/api/v1")

# Mount WebSocket routes
app.include_router(ws_router)


@app.get("/preview/{conversation_id}/{file_path:path}")
async def preview_file(conversation_id: str, file_path: str, db: AsyncSession = Depends(get_db)):
    return await PreviewService().file_response(db, conversation_id, file_path)


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    return api_error(str(exc.detail), exc.status_code)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(_, exc: RequestValidationError):
    return validation_api_error(exc)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "nailaude-backend"}
