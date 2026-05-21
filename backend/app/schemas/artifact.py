"""Artifact schemas"""
from pydantic import BaseModel


class ArtifactFileSchema(BaseModel):
    name: str
    content: str
    language: str = ""


class ArtifactResponse(BaseModel):
    id: str
    message_id: str
    type: str
    title: str
    files: list[ArtifactFileSchema]
    version: int
    preview_url: str
    created_at: str

    class Config:
        from_attributes = True
