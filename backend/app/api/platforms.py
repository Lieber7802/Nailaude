"""
Platform management routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import api_success, raise_api_error
from app.api.serializers import serialize_platform
from app.database import get_db
from app.models.agent import AgentPlatform
from app.services.seed import seed_builtin_data

router = APIRouter()


@router.get("")
async def list_platforms(db: AsyncSession = Depends(get_db)):
    """List available agent platforms"""
    await seed_builtin_data(db)
    result = await db.scalars(select(AgentPlatform).order_by(AgentPlatform.id.asc()))
    return api_success([serialize_platform(platform) for platform in result.all()])


@router.get("/{platform_id}")
async def get_platform(platform_id: str, db: AsyncSession = Depends(get_db)):
    """Get platform details"""
    await seed_builtin_data(db)
    platform = await db.get(AgentPlatform, platform_id)
    if platform is None:
        raise_api_error("Platform not found", 404)
    return api_success(serialize_platform(platform))


@router.post("/{platform_id}/healthcheck")
async def check_platform_health(platform_id: str, db: AsyncSession = Depends(get_db)):
    """Check platform health status"""
    await seed_builtin_data(db)
    platform = await db.get(AgentPlatform, platform_id)
    if platform is None:
        raise_api_error("Platform not found", 404)
    return api_success({"status": platform.status, "version": "mock"})
