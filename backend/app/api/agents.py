"""
Agent CRUD routes
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_agents():
    """List all agents"""
    return {"data": [], "total": 0}


@router.post("")
async def create_agent():
    """Create a new agent"""
    return {"status": "not implemented"}


@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent by ID"""
    return {"status": "not implemented", "id": agent_id}


@router.patch("/{agent_id}")
async def update_agent(agent_id: str):
    """Update agent"""
    return {"status": "not implemented", "id": agent_id}


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete agent"""
    return {"status": "not implemented", "id": agent_id}
