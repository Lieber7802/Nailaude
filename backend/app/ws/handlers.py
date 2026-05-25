"""
WebSocket endpoint handlers
"""
import json
from json import JSONDecodeError

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.mock import MockAdapter
from app.api.serializers import serialize_artifact, serialize_message
from app.database import get_db
from app.models.agent import Agent
from app.models.artifact import Artifact
from app.models.conversation import Conversation
from app.models.message import Message
from app.services.seed import seed_builtin_data
from app.ws.manager import manager

ws_router = APIRouter()


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
    agent = await resolve_agent(db, conversation, payload.get("mentions") or [])
    if agent is None:
        await send_error(websocket, "Agent not found", recoverable=False)
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

    agent_message = Message(
        conversation_id=conversation_id,
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
    await db.refresh(user_message)
    await db.refresh(agent_message)

    user_message_data = serialize_message(user_message)
    if payload.get("clientMessageId"):
        user_message_data["clientMessageId"] = payload.get("clientMessageId")
    await manager.send_personal(websocket, {"type": "user_message", "data": user_message_data})

    await manager.send_personal(
        websocket,
        {"type": "agent_thinking", "data": {"agentId": agent.id, "agentName": agent.name}},
    )

    adapter = MockAdapter(response_delay=0)
    content_parts: list[str] = []
    try:
        async for event in adapter.run_task(
            conversation.work_dir,
            content,
            {"agentName": agent.name},
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
            elif event.type == "file_created":
                artifact = Artifact(
                    message_id=agent_message.id,
                    type="code",
                    title=str(event.metadata.get("title") or event.content),
                    files=event.metadata.get("files") or [],
                    diff_data=None,
                    version=1,
                    previous_version_id=None,
                    preview_url=event.metadata.get("previewUrl") or "",
                )
                db.add(artifact)
                await db.commit()
                await db.refresh(artifact)
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
                await send_error(websocket, event.content, message_id=agent_message.id, recoverable=True)
            elif event.type == "done":
                agent_message.content = "".join(content_parts)
                await db.commit()
                await manager.send_personal(
                    websocket,
                    {"type": "message_done", "data": {"messageId": agent_message.id, "agentName": agent.name}},
                )
    except Exception as exc:
        agent_message.content = "".join(content_parts)
        agent_message.meta = {**(agent_message.meta or {}), "status": "error", "error": str(exc)}
        await db.commit()
        await send_error(websocket, f"Mock stream failed: {exc}", message_id=agent_message.id, recoverable=False)


async def resolve_agent(db: AsyncSession, conversation: Conversation, mentions: list[dict]) -> Agent | None:
    if mentions:
        agent_id = mentions[0].get("agentId") or mentions[0].get("agent_id")
        if agent_id:
            return await db.get(Agent, agent_id)

    if conversation.participant_ids:
        return await db.get(Agent, conversation.participant_ids[0])

    return await db.scalar(select(Agent).order_by(Agent.created_at.asc()))


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
