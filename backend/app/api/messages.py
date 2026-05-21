"""
Message routes (nested under conversations)
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/{conversation_id}/messages")
async def list_messages(conversation_id: str):
    """List messages in a conversation"""
    return {"data": [], "conversation_id": conversation_id}


@router.post("/{conversation_id}/messages")
async def send_message(conversation_id: str):
    """Send a message (REST fallback, WebSocket preferred)"""
    return {"status": "not implemented", "conversation_id": conversation_id}
