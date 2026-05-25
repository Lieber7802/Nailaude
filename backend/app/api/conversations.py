"""
Conversation CRUD routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import api_success, paginated, raise_api_error
from app.api.serializers import serialize_conversation
from app.database import get_db
from app.models.artifact import Artifact
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.conversation import ConversationCreate, ConversationUpdate

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

    query = select(Conversation)
    count_query = select(func.count()).select_from(Conversation)
    if search:
        query = query.where(Conversation.title.contains(search))
        count_query = count_query.where(Conversation.title.contains(search))

    total = await db.scalar(count_query)
    result = await db.scalars(
        query.order_by(Conversation.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    items = [serialize_conversation(conversation) for conversation in result.all()]
    return api_success(paginated(items, total or 0, page, page_size))


@router.post("")
async def create_conversation(payload: ConversationCreate, db: AsyncSession = Depends(get_db)):
    """Create a new conversation"""
    conversation = Conversation(
        title=payload.title,
        type=payload.type,
        work_dir=payload.work_dir,
        participant_ids=payload.participant_ids,
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return api_success(serialize_conversation(conversation))


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
