"""
Conversation CRUD routes
"""
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import api_success, paginated, raise_api_error
from app.api.serializers import serialize_artifact, serialize_conversation
from app.database import get_db
from app.models.agent import Agent
from app.models.artifact import Artifact
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.conversation import ConversationCreate, ConversationUpdate, WINDOWS_WORKSPACE_PATTERN
from app.services.workspace_paths import resolve_workspace_path

router = APIRouter()


@router.get("")
async def list_conversations(
    page: int = 1,
    pageSize: int = 20,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List all conversations"""
    page = max(page, 1)
    page_size = max(min(pageSize, 100), 1)

    latest_message_at = (
        select(func.max(Message.created_at))
        .where(Message.conversation_id == Conversation.id)
        .correlate(Conversation)
        .scalar_subquery()
    )
    latest_message_content = (
        select(Message.content)
        .where(Message.conversation_id == Conversation.id)
        .order_by(Message.created_at.desc())
        .limit(1)
        .correlate(Conversation)
        .scalar_subquery()
    )
    latest_message_role = (
        select(Message.role)
        .where(Message.conversation_id == Conversation.id)
        .order_by(Message.created_at.desc())
        .limit(1)
        .correlate(Conversation)
        .scalar_subquery()
    )
    latest_agent_name = (
        select(Agent.name)
        .join(Message, Message.agent_id == Agent.id)
        .where(Message.conversation_id == Conversation.id)
        .order_by(Message.created_at.desc())
        .limit(1)
        .correlate(Conversation)
        .scalar_subquery()
    )
    query = select(Conversation, latest_message_content, latest_message_role, latest_agent_name, latest_message_at)
    count_query = select(func.count()).select_from(Conversation)
    if search:
        search_filter = or_(Conversation.title.contains(search), latest_message_content.contains(search))
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    total = await db.scalar(count_query)
    result = await db.execute(
        query.order_by(func.coalesce(latest_message_at, Conversation.updated_at).desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = [
        serialize_conversation(
            conversation,
            last_message=format_last_message(message_content, message_role, agent_name),
        )
        for conversation, message_content, message_role, agent_name, _message_at in result.all()
    ]
    return api_success(paginated(items, total or 0, page, page_size))


@router.post("")
async def create_conversation(payload: ConversationCreate, db: AsyncSession = Depends(get_db)):
    """Create a new conversation"""
    await validate_participants(payload.participant_ids, db)
    work_dir = payload.work_dir or f"workspaces/{uuid.uuid4().hex[:12]}"
    if payload.work_dir:
        ensure_workspace_directory(payload.work_dir)
    else:
        ensure_workspace_directory(work_dir)
    conversation = Conversation(
        title=payload.title,
        type=payload.type,
        work_dir=work_dir,
        participant_ids=payload.participant_ids,
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return api_success(serialize_conversation(conversation))


@router.get("/{conversation_id}/artifacts")
async def list_conversation_artifacts(
    conversation_id: str,
    type: list[str] | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """List artifacts for a conversation."""
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        raise_api_error("Conversation not found", 404)

    query = (
        select(Artifact)
        .join(Message, Artifact.message_id == Message.id)
        .where(Message.conversation_id == conversation_id)
        .order_by(Artifact.created_at.asc())
    )
    if type:
        query = query.where(Artifact.type.in_(type))
    result = await db.scalars(query)
    return api_success([serialize_artifact(artifact) for artifact in result.all()])


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    """Get conversation by ID"""
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        raise_api_error("Conversation not found", 404)
    return api_success(serialize_conversation(conversation))


@router.patch("/{conversation_id}")
async def update_conversation(
    conversation_id: str,
    payload: ConversationUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update conversation"""
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        raise_api_error("Conversation not found", 404)

    updates = payload.model_dump(exclude_unset=True)
    if "participant_ids" in updates:
        await validate_participants(updates["participant_ids"], db)
    if "work_dir" in updates:
        ensure_workspace_directory(updates["work_dir"] or "")
    for key, value in updates.items():
        setattr(conversation, key, value)

    await db.commit()
    await db.refresh(conversation)
    return api_success(serialize_conversation(conversation))


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    """Delete conversation"""
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        raise_api_error("Conversation not found", 404)

    message_ids = select(Message.id).where(Message.conversation_id == conversation_id)
    await db.execute(delete(Artifact).where(Artifact.message_id.in_(message_ids)))
    await db.execute(delete(Message).where(Message.conversation_id == conversation_id))
    await db.delete(conversation)
    await db.commit()
    return api_success({"id": conversation_id})


def format_last_message(content: str | None, role: str | None, agent_name: str | None) -> str | None:
    if content is None:
        return None
    prefix = "你" if role == "user" else agent_name or "Agent"
    compact_content = " ".join(content.split())
    if len(compact_content) > 80:
        compact_content = f"{compact_content[:77]}..."
    return f"{prefix}: {compact_content}"


async def validate_participants(participant_ids: list[str], db: AsyncSession) -> None:
    if not participant_ids:
        raise_api_error("participantIds must include at least one agent", 400)
    existing = await db.scalars(select(Agent.id).where(Agent.id.in_(participant_ids)))
    existing_ids = set(existing.all())
    missing_ids = [agent_id for agent_id in participant_ids if agent_id not in existing_ids]
    if missing_ids:
        raise_api_error("Participant agent not found", 400)


def ensure_workspace_directory(work_dir: str) -> None:
    if not work_dir or WINDOWS_WORKSPACE_PATTERN.match(work_dir):
        return
    resolve_workspace_path(work_dir).mkdir(parents=True, exist_ok=True)
