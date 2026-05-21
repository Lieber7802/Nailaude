"""
Artifact routes
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/{artifact_id}")
async def get_artifact(artifact_id: str):
    """Get artifact by ID"""
    return {"status": "not implemented", "id": artifact_id}


@router.get("")
async def list_artifacts(message_id: str | None = None):
    """List artifacts, optionally filtered by message"""
    return {"data": [], "message_id": message_id}
