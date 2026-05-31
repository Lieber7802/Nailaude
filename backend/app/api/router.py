"""
API Router - aggregates all sub-routers
"""
from fastapi import APIRouter

from app.api.conversations import router as conversations_router
from app.api.messages import router as messages_router
from app.api.agents import router as agents_router
from app.api.platforms import router as platforms_router
from app.api.artifacts import router as artifacts_router
from app.api.orchestrator import router as orchestrator_router

api_router = APIRouter()

api_router.include_router(conversations_router, prefix="/conversations", tags=["conversations"])
api_router.include_router(messages_router, prefix="/conversations", tags=["messages"])
api_router.include_router(agents_router, prefix="/agents", tags=["agents"])
api_router.include_router(platforms_router, prefix="/platforms", tags=["platforms"])
api_router.include_router(artifacts_router, prefix="/artifacts", tags=["artifacts"])
api_router.include_router(orchestrator_router, prefix="/conversations", tags=["orchestrator"])
