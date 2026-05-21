"""
Conversation CRUD routes
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_conversations():
    """List all conversations"""
    return {"data": [], "total": 0}


@router.post("")
async def create_conversation():
    """Create a new conversation"""
    return {"status": "not implemented"}


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation by ID"""
    return {"status": "not implemented", "id": conversation_id}


@router.patch("/{conversation_id}")
async def update_conversation(conversation_id: str):
    """Update conversation"""
    return {"status": "not implemented", "id": conversation_id}


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete conversation"""
    return {"status": "not implemented", "id": conversation_id}
