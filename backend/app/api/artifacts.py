"""
Artifact routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import api_success, raise_api_error
from app.api.serializers import serialize_artifact
from app.database import get_db
from app.models.artifact import Artifact

router = APIRouter()


@router.get("/{artifact_id}")
async def get_artifact(artifact_id: str, db: AsyncSession = Depends(get_db)):
    """Get artifact by ID"""
    artifact = await db.get(Artifact, artifact_id)
    if artifact is None:
        raise_api_error("Artifact not found", 404)
    return api_success(serialize_artifact(artifact))


@router.get("/{artifact_id}/versions")
async def get_artifact_versions(artifact_id: str, db: AsyncSession = Depends(get_db)):
    """Get a compact version chain for an artifact."""
    artifact = await db.get(Artifact, artifact_id)
    if artifact is None:
        raise_api_error("Artifact not found", 404)
    result = await db.scalars(
        select(Artifact)
        .where(Artifact.message_id == artifact.message_id, Artifact.title == artifact.title)
        .order_by(Artifact.version.asc(), Artifact.created_at.asc())
    )
    return api_success(
        [
            {"id": item.id, "version": item.version, "createdAt": item.created_at.isoformat()}
            for item in result.all()
        ]
    )


@router.get("")
async def list_artifacts(message_id: str | None = None, db: AsyncSession = Depends(get_db)):
    """List artifacts, optionally filtered by message"""
    query = select(Artifact)
    if message_id:
        query = query.where(Artifact.message_id == message_id)
    result = await db.scalars(query.order_by(Artifact.created_at.asc()))
    artifacts = [serialize_artifact(artifact) for artifact in result.all()]
    return api_success(artifacts)
