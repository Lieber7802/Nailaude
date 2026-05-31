"""
Agent CRUD routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import api_success, raise_api_error
from app.api.serializers import serialize_agent
from app.database import get_db
from app.models.agent import Agent, AgentPlatform
from app.schemas.agent import AgentCreate, AgentUpdate
from app.services.seed import seed_builtin_data

router = APIRouter()


@router.get("")
async def list_agents(db: AsyncSession = Depends(get_db)):
    """List all agents"""
    await seed_builtin_data(db)
    result = await db.scalars(select(Agent).order_by(Agent.is_builtin.desc(), Agent.created_at.asc()))
    return api_success([serialize_agent(agent) for agent in result.all()])


@router.post("")
async def create_agent(payload: AgentCreate, db: AsyncSession = Depends(get_db)):
    """Create a new agent"""
    await seed_builtin_data(db)
    platform = await db.get(AgentPlatform, payload.platform_id)
    if platform is None:
        raise_api_error("Platform not found", 400)

    agent = Agent(
        name=payload.name,
        avatar=payload.avatar,
        description=payload.description,
        capabilities=payload.capabilities,
        system_instruction=payload.system_instruction,
        platform_id=payload.platform_id,
        is_builtin=False,
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return api_success(serialize_agent(agent))


@router.get("/{agent_id}")
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Get agent by ID"""
    await seed_builtin_data(db)
    agent = await db.get(Agent, agent_id)
    if agent is None:
        raise_api_error("Agent not found", 404)
    return api_success(serialize_agent(agent))


@router.patch("/{agent_id}")
async def update_agent(agent_id: str, payload: AgentUpdate, db: AsyncSession = Depends(get_db)):
    """Update agent"""
    return await _update_agent(agent_id, payload, db)


@router.put("/{agent_id}")
async def put_agent(agent_id: str, payload: AgentUpdate, db: AsyncSession = Depends(get_db)):
    """Update agent"""
    return await _update_agent(agent_id, payload, db)


async def _update_agent(agent_id: str, payload: AgentUpdate, db: AsyncSession):
    agent = await db.get(Agent, agent_id)
    if agent is None:
        raise_api_error("Agent not found", 404)

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(agent, key, value)

    await db.commit()
    await db.refresh(agent)
    return api_success(serialize_agent(agent))


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Delete agent"""
    agent = await db.get(Agent, agent_id)
    if agent is None:
        raise_api_error("Agent not found", 404)
    if agent.is_builtin:
        raise_api_error("Builtin agents cannot be deleted", 400)

    await db.delete(agent)
    await db.commit()
    return api_success({"id": agent_id})
