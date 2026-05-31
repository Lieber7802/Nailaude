"""Read-only collaboration state API for the M3 workspace UI."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import api_success, raise_api_error
from app.database import get_db
from app.models.conversation import Conversation
from app.services.project_state import ProjectStateService, serialize_project_state
from app.services.team_protocol import TeamProtocolService, serialize_team_board

router = APIRouter()


@router.get("/{conversation_id}/project-state")
async def get_project_state(conversation_id: str, db: AsyncSession = Depends(get_db)):
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        raise_api_error("Conversation not found", 404)
    service = ProjectStateService(db)
    state = await service.get_state(conversation_id)
    if state is None:
        state = await service.refresh(conversation)
    return api_success(serialize_project_state(state))


@router.get("/{conversation_id}/team-board")
async def get_team_board(conversation_id: str, db: AsyncSession = Depends(get_db)):
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        raise_api_error("Conversation not found", 404)
    board = await TeamProtocolService(db).get_team_board(conversation_id)
    return api_success(serialize_team_board(board))
