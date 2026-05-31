"""
WebSocket endpoint handlers
"""
import json
from json import JSONDecodeError
from typing import TypedDict

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.mock import MockAdapter
from app.api.serializers import serialize_artifact, serialize_message
from app.database import get_db
from app.models.agent import Agent
from app.models.conversation import Conversation
from app.models.message import Message
from app.services.agent_manager import AgentManagerService
from app.services.artifact_service import ArtifactService
from app.services.orchestrator import OrchestratorService
from app.services.seed import seed_builtin_data
from app.ws.manager import manager

ws_router = APIRouter()


class StreamResult(TypedDict):
    status: str
    content: str
    error: str | None


@ws_router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Main WebSocket endpoint for real-time messaging."""
    await manager.connect(websocket, conversation_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except JSONDecodeError:
                await send_error(websocket, "Invalid JSON payload", recoverable=True)
                continue
            if message.get("type") == "send_message":
                await handle_send_message(websocket, conversation_id, message.get("data") or {}, db)
            elif message.get("type") == "stop_generation":
                await send_error(websocket, "Stop generation is not available in Mock mode yet", recoverable=True)
            else:
                await send_error(websocket, "Unsupported WebSocket message type", recoverable=True)
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        try:
            await send_error(websocket, f"WebSocket error: {exc}", recoverable=False)
        except Exception:
            pass
    finally:
        manager.disconnect(websocket, conversation_id)


async def handle_send_message(websocket: WebSocket, conversation_id: str, payload: dict, db: AsyncSession) -> None:
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        await send_error(websocket, "Conversation not found", recoverable=False)
        return

    await seed_builtin_data(db)
    try:
        agents = await resolve_dispatch_agents(db, conversation, payload.get("mentions") or [])
    except ValueError as exc:
        await send_error(websocket, str(exc), recoverable=True)
        return
    if not agents:
        await send_error(websocket, "Conversation has no participants", recoverable=False)
        return

    content = str(payload.get("content", ""))
    if not content.strip():
        await send_error(websocket, "Message content must not be empty", recoverable=True)
        return

    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        agent_id=None,
        content=content,
        content_type="text",
        mentions=payload.get("mentions") or [],
        parent_message_id=payload.get("parentMessageId"),
        meta={},
    )
    db.add(user_message)
    await db.flush()

    await db.commit()
    await db.refresh(user_message)

    user_message_data = serialize_message(user_message)
    if payload.get("clientMessageId"):
        user_message_data["clientMessageId"] = payload.get("clientMessageId")
    await manager.send_personal(websocket, {"type": "user_message", "data": user_message_data})

    orchestrator = OrchestratorService()
    plan = await orchestrator.build_dispatch_plan(conversation, content, payload.get("mentions") or [], agents)
    await send_orchestrator_status(websocket, "dispatching", plan)

    agent_manager = AgentManagerService()
    for task in plan["tasks"]:
        plan = orchestrator.mark_task(plan, task["id"], "running")
        await send_orchestrator_status(websocket, "executing", plan)
        agent = next((item for item in agents if item.id == task["agentId"]), None)
        if agent is None:
            plan = orchestrator.mark_task(plan, task["id"], "failed", "Agent not found")
            await send_orchestrator_status(websocket, "executing", plan)
            continue

        adapter = MockAdapter(response_delay=0) if agent.platform_id == "mock" else await agent_manager.get_adapter(agent.platform_id)
        result = await stream_agent_task(websocket, db, conversation, user_message, agent, adapter, content)
        task_status = "completed" if result["status"] == "success" else "failed"
        task_result = result["content"] if result["status"] == "success" else result["error"]
        plan = orchestrator.mark_task(plan, task["id"], task_status, task_result)
        await send_orchestrator_status(websocket, "executing", plan)

    await send_orchestrator_status(websocket, "summarizing", plan)


async def resolve_dispatch_agents(db: AsyncSession, conversation: Conversation, mentions: list[dict]) -> list[Agent]:
    participant_ids = list(conversation.participant_ids or [])
    if not participant_ids:
        return []

    agent_ids: list[str] = []
    for mention in mentions:
        agent_id = mention.get("agentId") or mention.get("agent_id")
        if agent_id and agent_id not in participant_ids:
            raise ValueError("Mentioned agent is not part of this conversation")
        if agent_id and agent_id not in agent_ids:
            agent_ids.append(agent_id)

    if not agent_ids:
        agent_ids = participant_ids

    agents = await db.scalars(select(Agent).where(Agent.id.in_(agent_ids)))
    agents_by_id = {agent.id: agent for agent in agents.all()}
    return [agents_by_id[agent_id] for agent_id in agent_ids if agent_id in agents_by_id]


async def send_orchestrator_status(websocket: WebSocket, status: str, plan: dict) -> None:
    await manager.send_personal(websocket, {"type": "orchestrator_status", "data": {"status": status, "tasks": plan["tasks"]}})


async def stream_agent_task(
    websocket: WebSocket,
    db: AsyncSession,
    conversation: Conversation,
    user_message: Message,
    agent: Agent,
    adapter,
    content: str,
) -> StreamResult:
    agent_message = Message(
        conversation_id=conversation.id,
        role="agent",
        agent_id=agent.id,
        content="",
        content_type="mixed",
        mentions=[],
        parent_message_id=user_message.id,
        meta={"platform": agent.platform_id},
    )
    db.add(agent_message)
    await db.commit()
    await db.refresh(agent_message)

    await manager.send_personal(
        websocket,
        {"type": "agent_thinking", "data": {"agentId": agent.id, "agentName": agent.name}},
    )

    content_parts: list[str] = []
    stream_status = "success"
    stream_error: str | None = None
    artifact_service = ArtifactService()
    try:
        async for event in adapter.run_task(
            conversation.work_dir,
            content,
            {"agentName": agent.name, "conversationId": conversation.id, "workDir": conversation.work_dir},
        ):
            if event.type == "text_delta":
                content_parts.append(event.content)
                await manager.send_personal(
                    websocket,
                    {
                        "type": "text_delta",
                        "data": {"messageId": agent_message.id, "agentName": agent.name, "delta": event.content},
                    },
                )
            elif event.type in {"file_created", "file_modified"}:
                artifacts = await artifact_service.create_from_agent_event(
                    db,
                    message_id=agent_message.id,
                    conversation_id=conversation.id,
                    work_dir=conversation.work_dir,
                    event=event,
                )
                for artifact in artifacts:
                    await manager.send_personal(
                        websocket,
                        {
                            "type": "artifact",
                            "data": {"messageId": agent_message.id, "artifact": serialize_artifact(artifact)},
                        },
                    )
            elif event.type == "team_note":
                await manager.send_personal(
                    websocket,
                    {
                        "type": "team_activity",
                        "data": {
                            "fromAgent": event.metadata.get("fromAgent", agent.name),
                            "to": event.metadata.get("to", "all"),
                            "content": event.content,
                            "noteType": event.metadata.get("noteType", "decision"),
                        },
                    },
                )
            elif event.type == "error":
                stream_status = "failed"
                stream_error = event.content
                await send_error(websocket, event.content, message_id=agent_message.id, recoverable=True)
            elif event.type == "done":
                agent_message.content = "".join(content_parts)
                if stream_error:
                    agent_message.meta = {**(agent_message.meta or {}), "status": "error", "error": stream_error}
                await db.commit()
                if stream_status == "success":
                    await manager.send_personal(
                        websocket,
                        {"type": "message_done", "data": {"messageId": agent_message.id, "agentName": agent.name}},
                    )
    except Exception as exc:
        stream_status = "failed"
        platform_label = "Mock" if agent.platform_id == "mock" else agent.platform_id
        stream_error = f"{platform_label} stream failed: {exc}"
        agent_message.content = "".join(content_parts)
        agent_message.meta = {**(agent_message.meta or {}), "status": "error", "error": stream_error}
        await db.commit()
        await send_error(websocket, stream_error, message_id=agent_message.id, recoverable=False)
    return {"status": stream_status, "content": "".join(content_parts), "error": stream_error}


async def send_error(
    websocket: WebSocket,
    error: str,
    message_id: str | None = None,
    recoverable: bool = True,
) -> None:
    data = {"error": error, "recoverable": recoverable}
    if message_id:
        data["messageId"] = message_id
    await manager.send_personal(websocket, {"type": "error", "data": data})
