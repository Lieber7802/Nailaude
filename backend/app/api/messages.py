"""
Message routes (nested under conversations)
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import api_success, paginated, raise_api_error
from app.api.serializers import serialize_message
from app.database import get_db
from app.models.agent import Agent
from app.models.artifact import Artifact
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.message import MessageCreate

router = APIRouter()


@router.get("/{conversation_id}/messages")
async def list_messages(
    conversation_id: str,
    page: int = 1,
    pageSize: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """List messages in a conversation"""
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        raise_api_error("Conversation not found", 404)

    page = max(page, 1)
    page_size = max(min(pageSize, 100), 1)
    total = await db.scalar(select(func.count()).select_from(Message).where(Message.conversation_id == conversation_id))
    result = await db.scalars(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    messages = result.all()
    message_ids = [message.id for message in messages]
    agent_ids = [message.agent_id for message in messages if message.agent_id]

    artifacts_by_message: dict[str, list[Artifact]] = {message_id: [] for message_id in message_ids}
    if message_ids:
        artifacts = await db.scalars(
            select(Artifact).where(Artifact.message_id.in_(message_ids)).order_by(Artifact.created_at.asc())
        )
        for artifact in artifacts.all():
            artifacts_by_message.setdefault(artifact.message_id, []).append(artifact)

    agent_names: dict[str, str] = {}
    if agent_ids:
        agents = await db.scalars(select(Agent).where(Agent.id.in_(agent_ids)))
        agent_names = {agent.id: agent.name for agent in agents.all()}

    items = [
        serialize_message(
            message,
            artifacts=artifacts_by_message.get(message.id, []),
            agent_name=agent_names.get(message.agent_id or ""),
        )
        for message in messages
    ]
    return api_success(paginated(items, total or 0, page, page_size))


@router.post("/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
):
    """Send a message (REST fallback, WebSocket preferred)"""
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        raise_api_error("Conversation not found", 404)

    message = Message(
        conversation_id=conversation_id,
        role="user",
        agent_id=None,
        content=payload.content,
        content_type="text",
        mentions=[mention.model_dump(by_alias=True) for mention in payload.mentions],
        parent_message_id=payload.parent_message_id,
        meta={},
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return api_success(serialize_message(message))
