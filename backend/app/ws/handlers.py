"""
WebSocket endpoint handlers
"""
import json
import asyncio
from collections import defaultdict
from json import JSONDecodeError
from typing import TypedDict

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.adapters.base import AgentAdapter
from app.adapters.mock import MockAdapter
from app.api.serializers import serialize_artifact, serialize_message
from app.database import get_db
from app.models.agent import Agent
from app.models.conversation import Conversation
from app.models.message import Message
from app.services.artifact_service import ArtifactService
from app.services.orchestrator import OrchestratorService
from app.services.agent_manager import AgentManagerService
from app.services.handoff_builder import HandoffBuilder
from app.services.orchestrator_planner import OrchestratorPlanner, PlannerFailure
from app.services.orchestrator_queue import OrchestratorQueue, QueueFullError
from app.services.orchestrator_runtime import OrchestratorRuntime
from app.services.orchestrator_state import persist_snapshot, reconciled_snapshot_for_conversation
from app.services.seed import seed_builtin_data
from app.services.project_state import ProjectStateService, serialize_project_state
from app.services.team_protocol import TeamProtocolService, serialize_team_board
from app.ws.manager import manager

ws_router = APIRouter()
runtime = OrchestratorRuntime()
agent_manager = AgentManagerService()
orchestrator_queue = OrchestratorQueue()
pending_jobs: dict[str, dict] = {}
paused_jobs: dict[tuple[str, str], dict] = {}
queue_workers: dict[str, asyncio.Task] = {}
db_locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)


class StreamResult(TypedDict):
    status: str
    content: str
    error: str | None
    team_notes: list[dict]


@ws_router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Main WebSocket endpoint for real-time messaging."""
    await manager.connect(websocket, conversation_id)
    if conversation_id not in manager.latest_snapshots:
        snapshot = await reconciled_snapshot_for_conversation(db, conversation_id)
        if snapshot:
            event = {"type": "orchestrator_status", "data": snapshot}
            manager.record_snapshot(conversation_id, event)
            await manager.send_personal(websocket, event)
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
            elif message.get("type") == "orchestrator_input_response":
                await handle_input_response(websocket, conversation_id, message.get("data") or {}, db)
            elif message.get("type") == "orchestrator_approval_response":
                await handle_approval_response(websocket, conversation_id, message.get("data") or {}, db)
            elif message.get("type") == "stop_generation":
                active_run_id = orchestrator_queue.active(conversation_id)
                if active_run_id:
                    runtime.cancel(active_run_id)
                else:
                    await send_error(websocket, "No active run to cancel", recoverable=True)
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
    async with db_locks[conversation_id]:
        await handle_send_message_locked(websocket, conversation_id, payload, db)


async def handle_send_message_locked(websocket: WebSocket, conversation_id: str, payload: dict, db: AsyncSession) -> None:
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

    run_id = user_message.id
    job = {
        "run_id": run_id,
        "conversation": conversation,
        "content": content,
        "mentions": payload.get("mentions") or [],
        "agents": agents,
        "session_factory": async_sessionmaker(bind=db.bind, expire_on_commit=False),
        "user_message": user_message,
        "sequence": 0,
        "clarification_answers": [],
        "planner_result": None,
        "approval_granted": False,
    }
    try:
        await enqueue_job(conversation_id, job, db, db_locked=True)
    except QueueFullError as exc:
        await send_error(websocket, str(exc), recoverable=True)


async def enqueue_job(conversation_id: str, job: dict, db: AsyncSession, *, db_locked: bool = False) -> None:
    run_id = job["run_id"]
    queue_position = orchestrator_queue.enqueue(conversation_id, run_id)
    job["sequence"] = int(job.get("sequence") or 0) + 1
    pending_jobs[run_id] = job
    queued_snapshot = queued_status(run_id, queue_position, job["sequence"])
    if db_locked:
        await persist_snapshot(db, conversation_id, job["user_message"].id, queued_snapshot)
    else:
        async with db_locks[conversation_id]:
            await persist_snapshot(db, conversation_id, job["user_message"].id, queued_snapshot)
    event = {"type": "orchestrator_status", "data": queued_snapshot}
    manager.record_snapshot(conversation_id, event)
    await manager.broadcast(conversation_id, event)
    worker = queue_workers.get(conversation_id)
    if worker is None or worker.done():
        queue_workers[conversation_id] = asyncio.create_task(drain_conversation_queue(conversation_id))


async def handle_input_response(websocket: WebSocket, conversation_id: str, payload: dict, db: AsyncSession) -> None:
    run_id = str(payload.get("runId") or "")
    key = (conversation_id, run_id)
    job = paused_jobs.get(key)
    if job is None:
        await send_error(websocket, "Paused orchestrator run not found", recoverable=True)
        return
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None or conversation.id != job["conversation"].id:
        await send_error(websocket, "Paused orchestrator run does not belong to this conversation", recoverable=True)
        return

    planner_result = job.get("planner_result") or {}
    answers = payload.get("answers") or {}
    if planner_result.get("status") == "needs_clarification":
        required_ids = {str(question["id"]) for question in planner_result.get("questions") or []}
        if required_ids - set(answers):
            await send_error(websocket, "Please answer all clarification questions before submitting", recoverable=True)
            return

    approved_agent_ids = [str(item) for item in payload.get("approvedAgentIds") or []]
    if approved_agent_ids:
        agents = await db.scalars(select(Agent).where(Agent.id.in_(approved_agent_ids)))
        valid_agent_ids = {agent.id for agent in agents.all()}
        if valid_agent_ids != set(approved_agent_ids):
            await send_error(websocket, "Recommended agent not found", recoverable=True)
            return
        conversation.participant_ids = list(dict.fromkeys([*(conversation.participant_ids or []), *approved_agent_ids]))
        await db.commit()

    if answers:
        job["clarification_answers"] = [*(job.get("clarification_answers") or []), dict(answers)]
    job["conversation"] = conversation
    job["agents"] = await resolve_dispatch_agents(db, conversation, job["mentions"])
    job["planner_result"] = None
    job["approval_granted"] = False
    paused_jobs.pop(key, None)
    try:
        await enqueue_job(conversation_id, job, db)
    except QueueFullError as exc:
        paused_jobs[key] = job
        await send_error(websocket, str(exc), recoverable=True)


async def handle_approval_response(websocket: WebSocket, conversation_id: str, payload: dict, db: AsyncSession) -> None:
    run_id = str(payload.get("runId") or "")
    key = (conversation_id, run_id)
    job = paused_jobs.get(key)
    if job is None:
        await send_error(websocket, "Paused orchestrator run not found", recoverable=True)
        return
    if job["conversation"].id != conversation_id:
        await send_error(websocket, "Paused orchestrator run does not belong to this conversation", recoverable=True)
        return
    paused_jobs.pop(key, None)
    if not payload.get("approved"):
        await publish_job_snapshot(db, conversation_id, job, "cancelled", "Elevated write operation rejected")
        return
    job["approval_granted"] = True
    try:
        await enqueue_job(conversation_id, job, db)
    except QueueFullError as exc:
        paused_jobs[key] = job
        await send_error(websocket, str(exc), recoverable=True)


async def drain_conversation_queue(conversation_id: str) -> None:
    try:
        while run_id := orchestrator_queue.activate_next(conversation_id):
            job = pending_jobs.pop(run_id)
            try:
                async with job["session_factory"]() as worker_db:
                    await execute_job(conversation_id, {**job, "db": worker_db})
            finally:
                orchestrator_queue.complete_current(conversation_id)
    finally:
        queue_workers.pop(conversation_id, None)
        if orchestrator_queue.queued_count(conversation_id):
            queue_workers[conversation_id] = asyncio.create_task(drain_conversation_queue(conversation_id))


async def execute_job(conversation_id: str, job: dict) -> None:
    conversation = job["conversation"]
    content = job["content"]
    agents = job["agents"]
    db = job["db"]
    user_message = job["user_message"]
    planner_result = job.get("planner_result")
    if planner_result is None:
        await publish_job_snapshot(db, conversation_id, job, "planning", "Planning orchestrator run")
        try:
            planner_result = await plan_job(job, db)
        except PlannerFailure as exc:
            await publish_job_snapshot(db, conversation_id, job, "failed", "Planner failed")
            await broadcast_error(conversation_id, str(exc), recoverable=True)
            return
        if planner_result["status"] == "cannot_plan":
            await publish_job_snapshot(db, conversation_id, job, "failed", "Planner cannot execute this request")
            await broadcast_error(conversation_id, planner_result["reason"], recoverable=bool(planner_result.get("recoverable", True)))
            return
        if planner_result["status"] != "ready":
            await publish_job_snapshot(db, conversation_id, job, "awaiting_input", "Planner needs user input")
            job["planner_result"] = planner_result
            paused_jobs[(conversation_id, job["run_id"])] = job
            await manager.broadcast(
                conversation_id,
                {"type": "orchestrator_input_required", "data": {"runId": job["run_id"], "result": planner_result}},
            )
            return
        job["planner_result"] = planner_result
        await publish_job_snapshot(
            db,
            conversation_id,
            job,
            "validating",
            "Planner result validated",
            tasks=planner_result["tasks"],
            reasoning_summary=planner_result.get("reasoningSummary") or "",
        )
    approval_reason = elevated_write_approval_reason(planner_result["tasks"])
    if approval_reason and not job.get("approval_granted"):
        await publish_job_snapshot(
            db,
            conversation_id,
            job,
            "awaiting_approval",
            approval_reason,
            tasks=planner_result["tasks"],
            reasoning_summary=planner_result.get("reasoningSummary") or "",
        )
        paused_jobs[(conversation_id, job["run_id"])] = job
        await manager.broadcast(
            conversation_id,
            {
                "type": "orchestrator_approval_required",
                "data": {"runId": job["run_id"], "reason": approval_reason, "tasks": planner_result["tasks"]},
            },
        )
        return
    task_results: list[dict] = []
    handoff_builder = HandoffBuilder()
    async with db_locks[conversation_id]:
        board = await TeamProtocolService(db).get_team_board(conversation_id)
        project_summary = await ProjectStateService(db).build_context_summary(conversation_id)
    team_standards = list(board.code_standards or [])

    async def emit(snapshot: dict) -> None:
        async with db_locks[conversation_id]:
            await persist_snapshot(db, conversation_id, user_message.id, snapshot)
        event = {"type": "orchestrator_status", "data": snapshot}
        manager.record_snapshot(conversation_id, event)
        await manager.broadcast(conversation_id, event)

    async def execute_task(task: dict, workspace) -> dict:
        agent = next((item for item in agents if item.id == task["agentId"]), None)
        if agent is None:
            task_agent_name = task.get("agentName", "")
            if task_agent_name:
                agent = next((item for item in agents if item.name == task_agent_name), None)
        if agent is None:
            available = ", ".join(f"{a.id}({a.name})" for a in agents)
            return {
                "status": "failed",
                "summary": "",
                "error": f"Agent {task['agentId']} not found. Available: {available}",
                "teamNotes": [],
            }
        if agent.platform_id == "mock":
            adapter, selected_platform = MockAdapter(response_delay=0), "mock"
        else:
            adapter, selected_platform = await agent_manager.resolve_adapter(agent.platform_id)
        async with job["session_factory"]() as task_db:
            async with db_locks[conversation_id]:
                relevant_notes = await TeamProtocolService(task_db).relevant_notes(conversation_id, agent.id)
            dependency_results = [result for result in task_results if result["taskId"] in task["dependsOn"]]
            changed_files = sorted(
                {
                    path
                    for result in task_results
                    for path in (result.get("filesChanged") or [])
                }
            )
            handoff = handoff_builder.build(
                run_id=job["run_id"],
                batch_id=workspace.batch_id,
                workspace_path=workspace.path,
                snapshot_id=workspace.snapshot_id,
                task=task,
                project_summary=project_summary,
                team_standards=team_standards,
                relevant_team_notes=relevant_notes,
                dependency_results=dependency_results,
                navigation_hints={
                    "inspectFirst": changed_files[:20],
                    "changedFiles": changed_files,
                    "diffSummary": ", ".join(changed_files),
                },
            )
            result = await stream_agent_task(
                conversation_id,
                task_db,
                conversation,
                user_message,
                agent,
                adapter,
                task["instruction"],
                workspace.path,
                handoff,
                cancel_event=workspace.cancel_event,
            )
            execution_warnings = [] if selected_platform == agent.platform_id else [f"Adapter downgraded to {selected_platform}"]
            if result["status"] == "failed" and task["accessMode"] == "read" and selected_platform != "mock":
                try:
                    fallback, fallback_platform = await agent_manager.resolve_adapter(
                        agent.platform_id,
                        excluded={selected_platform},
                    )
                except RuntimeError:
                    fallback = None
                if fallback is not None:
                    execution_warnings.append(
                        f"Adapter {selected_platform} failed during execution; retried with {fallback_platform}"
                    )
                    result = await stream_agent_task(
                        conversation_id,
                        task_db,
                        conversation,
                        user_message,
                        agent,
                        fallback,
                        task["instruction"],
                        workspace.path,
                        handoff,
                        cancel_event=workspace.cancel_event,
                    )
        task_result = {
            "taskId": task["id"],
            "agentId": agent.id,
            "batchId": workspace.batch_id,
            "status": result["status"],
            "summary": result["content"],
            "error": result["error"],
            "teamNotes": result["team_notes"],
            "warnings": execution_warnings,
        }
        task_results.append(task_result)
        return task_result

    async def refresh_shared_state(batch_results: list[dict], batch: dict) -> dict:
        nonlocal project_summary, team_standards
        async with db_locks[conversation_id]:
            team_service = TeamProtocolService(db)
            board = await team_service.merge_batch(conversation_id, batch_results)
            state = await ProjectStateService(db).refresh(conversation, batch_results)
            project_summary = state.progress_summary
            team_standards = list(board.code_standards or [])
        await manager.broadcast(conversation_id, {"type": "team_board_updated", "data": {"conversationId": conversation_id, "version": board.version}})
        await manager.broadcast(conversation_id, {"type": "project_state_updated", "data": {"conversationId": conversation_id, "version": state.version}})
        return {
            "teamBoardVersion": board.version,
            "projectStateVersion": state.version,
            "warnings": [*team_service.warnings, *state.warnings],
        }

    await runtime.execute(
        run_id=job["run_id"],
        conversation_id=conversation_id,
        work_dir=conversation.work_dir or ".",
        tasks=planner_result["tasks"],
        executor=execute_task,
        emit=emit,
        reasoning_summary=planner_result["reasoningSummary"],
        initial_sequence=job["sequence"],
        refresh_shared_state=refresh_shared_state,
    )


async def plan_job(job: dict, db: AsyncSession) -> dict:
    agents = job["agents"]
    if all(agent.platform_id == "mock" for agent in agents):
        return await OrchestratorService().build_mock_planner_result(
            job["conversation"], job["content"], job["mentions"], agents
        )
    participant_ids = set(job["conversation"].participant_ids or [])
    participant_agents = await db.scalars(select(Agent).where(Agent.id.in_(participant_ids)))
    catalog = await db.scalars(select(Agent))
    participant_agent_list = participant_agents.all()
    catalog_agents = catalog.all()
    project_service = ProjectStateService(db)
    project_state = await project_service.get_state(job["conversation"].id)
    if project_state is None:
        project_state = await project_service.refresh(job["conversation"])
    team_board = await TeamProtocolService(db).get_team_board(job["conversation"].id)
    recent_messages = await db.scalars(
        select(Message)
        .where(Message.conversation_id == job["conversation"].id)
        .order_by(Message.created_at.desc())
        .limit(20)
    )
    recent_summary = [
        {"role": message.role, "content": message.content}
        for message in reversed(recent_messages.all())
    ]
    context = {
        "userRequest": job["content"],
        "mentions": job["mentions"],
        "clarificationAnswers": job.get("clarification_answers") or [],
        "participants": [
            {"id": agent.id, "name": agent.name, "description": agent.description, "capabilities": agent.capabilities}
            for agent in participant_agent_list
        ],
        "availableAgentCatalog": [
            {"id": agent.id, "name": agent.name, "description": agent.description, "capabilities": agent.capabilities}
            for agent in catalog_agents
        ],
        "projectPlanningSummary": serialize_project_state(project_state),
        "teamBoardSummary": serialize_team_board(team_board),
        "recentConversationSummary": recent_summary,
        "fileTreeSummary": list((project_state.file_tree or {}).get("paths") or [])[:500],
        "previousValidationErrors": [],
    }
    available_agent_ids = {agent.id for agent in catalog_agents}
    result = await OrchestratorPlanner().plan(context, participant_ids, available_agent_ids)
    return result.model_dump(by_alias=True)


def elevated_write_approval_reason(tasks: list[dict]) -> str | None:
    for task in tasks:
        if task.get("accessMode") != "write":
            continue
        risk_hints = task.get("riskHints") or {}
        if risk_hints.get("mayDeleteOrRenameFiles"):
            return "Write task may delete or rename files"
        if risk_hints.get("mayTouchConfigFiles"):
            return "Write task may modify configuration files"
        if int(risk_hints.get("estimatedFilesTouched") or 0) > 10:
            return "Write task may modify more than 10 files"
    return None


async def publish_job_snapshot(
    db: AsyncSession,
    conversation_id: str,
    job: dict,
    status: str,
    message: str,
    *,
    tasks: list[dict] | None = None,
    reasoning_summary: str = "",
) -> dict:
    job["sequence"] = int(job.get("sequence") or 0) + 1
    snapshot = status_snapshot(
        job["run_id"],
        job["sequence"],
        status,
        message,
        tasks=tasks,
        reasoning_summary=reasoning_summary,
    )
    async with db_locks[conversation_id]:
        await persist_snapshot(db, conversation_id, job["user_message"].id, snapshot)
    event = {"type": "orchestrator_status", "data": snapshot}
    manager.record_snapshot(conversation_id, event)
    await manager.broadcast(conversation_id, event)
    return snapshot


def status_snapshot(
    run_id: str,
    sequence: int,
    status: str,
    message: str,
    *,
    tasks: list[dict] | None = None,
    reasoning_summary: str = "",
) -> dict:
    from app.services.orchestrator_runtime import utc_timestamp

    now = utc_timestamp()
    return {
        "runId": run_id,
        "sequence": sequence,
        "status": status,
        "message": message,
        "reasoningSummary": reasoning_summary,
        "currentBatchIndex": None,
        "totalBatches": 0,
        "tasks": tasks or [],
        "batches": [],
        "warnings": [],
        "teamBoardVersion": 0,
        "projectStateVersion": 0,
        "createdAt": now,
        "updatedAt": now,
    }


def queued_status(run_id: str, queue_position: int, sequence: int = 1) -> dict:
    return {**status_snapshot(run_id, sequence, "queued", "Run queued"), "queuePosition": queue_position}


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
    conversation_id: str,
    db: AsyncSession,
    conversation: Conversation,
    user_message: Message,
    agent: Agent,
    adapter: AgentAdapter,
    content: str,
    work_dir: str,
    context: dict,
    cancel_event: asyncio.Event | None = None,
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
    async with db_locks[conversation_id]:
        db.add(agent_message)
        await db.commit()
        await db.refresh(agent_message)

    await manager.broadcast(
        conversation_id,
        {"type": "agent_thinking", "data": {"agentId": agent.id, "agentName": agent.name}},
    )

    content_parts: list[str] = []
    stream_status = "success"
    stream_error: str | None = None
    team_notes: list[dict] = []
    artifact_service = ArtifactService()
    try:
        async for event in adapter.run_task(
            work_dir,
            content,
            {
                **context,
                "agentName": agent.name,
                "conversationId": conversation.id,
                "workDir": work_dir,
                "_cancel_event": cancel_event,
            },
        ):
            if event.type == "text_delta":
                content_parts.append(event.content)
                await manager.broadcast(
                    conversation_id,
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
                    work_dir=work_dir,
                    event=event,
                )
                for artifact in artifacts:
                    await manager.broadcast(
                        conversation_id,
                        {
                            "type": "artifact",
                            "data": {"messageId": agent_message.id, "artifact": serialize_artifact(artifact)},
                        },
                    )
            elif event.type == "team_note":
                team_notes.append(
                    {
                        "type": event.metadata.get("noteType", "heads_up"),
                        "content": event.content,
                        "fromAgentId": agent.id,
                        "fromAgentName": event.metadata.get("fromAgent", agent.name),
                        "toType": "all" if event.metadata.get("to", "all") == "all" else "agent",
                    }
                )
                await manager.broadcast(
                    conversation_id,
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
                await broadcast_error(conversation_id, event.content, message_id=agent_message.id, recoverable=True)
            elif event.type == "done":
                agent_message.content = "".join(content_parts)
                if stream_error:
                    agent_message.meta = {**(agent_message.meta or {}), "status": "error", "error": stream_error}
                async with db_locks[conversation_id]:
                    await db.commit()
                if stream_status == "success":
                    await manager.broadcast(
                        conversation_id,
                        {"type": "message_done", "data": {"messageId": agent_message.id, "agentName": agent.name}},
                    )
    except Exception as exc:
        stream_status = "failed"
        stream_error = f"Agent stream failed: {exc}"
        agent_message.content = "".join(content_parts)
        agent_message.meta = {**(agent_message.meta or {}), "status": "error", "error": stream_error}
        async with db_locks[conversation_id]:
            await db.commit()
        await broadcast_error(conversation_id, stream_error, message_id=agent_message.id, recoverable=False)
    return {"status": stream_status, "content": "".join(content_parts), "error": stream_error, "team_notes": team_notes}


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


async def broadcast_error(
    conversation_id: str,
    error: str,
    message_id: str | None = None,
    recoverable: bool = True,
) -> None:
    data = {"error": error, "recoverable": recoverable}
    if message_id:
        data["messageId"] = message_id
    await manager.broadcast(conversation_id, {"type": "error", "data": data})
