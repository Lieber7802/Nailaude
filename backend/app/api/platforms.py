"""
Platform management routes
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_platforms():
    """List available agent platforms"""
    return {
        "data": [
            {"id": "mock", "name": "Mock Agent", "status": "available"},
            {"id": "opencode", "name": "OpenCode", "status": "not_installed"},
            {"id": "codex", "name": "Codex", "status": "not_installed"},
        ]
    }


@router.get("/{platform_id}")
async def get_platform(platform_id: str):
    """Get platform details"""
    return {"status": "not implemented", "id": platform_id}


@router.post("/{platform_id}/health")
async def check_platform_health(platform_id: str):
    """Check platform health status"""
    return {"status": "not implemented", "id": platform_id}
