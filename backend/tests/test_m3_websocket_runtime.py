import pytest
import shutil
import uuid
import asyncio
from pathlib import Path
from types import SimpleNamespace

from app.ws.manager import ConnectionManager
from app.schemas.conversation import WORKSPACE_ROOT
from app.adapters.base import AgentEvent
from app.services.agent_manager import AgentManagerService
from app.ws import handlers as ws_handlers


class FakeWebSocket:
    def __init__(self):
        self.messages = []
        self.accepted = False

    async def accept(self):
        self.accepted = True

    async def send_json(self, payload):
        self.messages.append(payload)


class FailingWebSocket(FakeWebSocket):
    async def send_json(self, payload):
        raise RuntimeError("disconnected")


@pytest.mark.asyncio
async def test_connection_manager_restores_latest_orchestrator_snapshot_on_connect():
    manager = ConnectionManager()
    snapshot = {"type": "orchestrator_status", "data": {"runId": "run-1", "sequence": 3}}
    manager.record_snapshot("conversation", snapshot)
    websocket = FakeWebSocket()

    await manager.connect(websocket, "conversation")

    assert websocket.accepted is True
    assert websocket.messages == [snapshot]


@pytest.mark.asyncio
async def test_connection_manager_broadcast_removes_failed_socket_and_reaches_healthy_socket():
    manager = ConnectionManager()
    failed = FailingWebSocket()
    healthy = FakeWebSocket()
    manager.active_connections["conversation"] = [failed, healthy]

    await manager.broadcast("conversation", {"type": "team_board_updated", "data": {"version": 2}})

    assert manager.active_connections["conversation"] == [healthy]
    assert healthy.messages == [{"type": "team_board_updated", "data": {"version": 2}}]


def test_group_websocket_emits_full_monotonic_runtime_snapshots(client, create_agent):
    work_dir = WORKSPACE_ROOT / f"pytest-runtime-{uuid.uuid4()}"
    work_dir.mkdir(parents=True)
    agents = [create_agent(), create_agent()]
    conversation = client.post(
        "/api/v1/conversations",
        json={"type": "group", "workDir": str(work_dir), "participantIds": [agents[0]["id"], agents[1]["id"]]},
    ).json()["data"]

    with client.websocket_connect(f"/ws/{conversation['id']}") as websocket:
        websocket.send_json({"type": "send_message", "data": {"content": "Build and review", "mentions": []}})
        snapshots = []
        for _ in range(30):
            event = websocket.receive_json()
            if event["type"] == "orchestrator_status":
                snapshots.append(event["data"])
                if event["data"]["status"] == "completed":
                    break

    assert snapshots[-1]["status"] == "completed"
    assert all(snapshot["runId"] for snapshot in snapshots)
    assert [snapshot["sequence"] for snapshot in snapshots] == sorted(snapshot["sequence"] for snapshot in snapshots)
    assert snapshots[-1]["batches"]
    shutil.rmtree(work_dir)


def test_group_opencode_preview_request_emits_webpage_artifact(client, monkeypatch, create_agent):
    work_dir = WORKSPACE_ROOT / f"pytest-opencode-preview-{uuid.uuid4()}"
    work_dir.mkdir(parents=True)

    class PreviewRepairAdapter:
        async def health_check(self):
            return True

        async def run_task(self, work_dir, instruction, context):
            Path(work_dir, "README.md").write_text("# Notes only\n", encoding="utf-8")
            Path(work_dir, "index.html").write_text("<!doctype html><h1>天气小程序</h1>\n", encoding="utf-8")
            yield AgentEvent(type="text_delta", content="OpenCode 已完成本次执行。\n检测到 2 个文件变更，已生成对应产物卡片。")
            yield AgentEvent(
                type="file_created",
                content="README.md",
                metadata={
                    "title": "README.md",
                    "files": [{"name": "README.md", "content": "# Notes only\n", "language": "markdown"}],
                    "previewUrl": None,
                },
            )
            yield AgentEvent(
                type="file_created",
                content="index.html",
                metadata={
                    "title": "index.html",
                    "files": [
                        {
                            "name": "index.html",
                            "content": "<!doctype html><h1>天气小程序</h1>\n",
                            "language": "html",
                        }
                    ],
                    "previewUrl": None,
                },
            )
            yield AgentEvent(type="done")

    monkeypatch.setattr(
        ws_handlers,
        "agent_manager",
        AgentManagerService(factories={"opencode": PreviewRepairAdapter, "llm": PreviewRepairAdapter, "mock": PreviewRepairAdapter}),
    )
    agents = [
        create_agent(platform_id="opencode", name="代码工匠 Opencode"),
        create_agent(platform_id="opencode", name="审查大师 Opencode"),
    ]
    conversation = client.post(
        "/api/v1/conversations",
        json={"type": "group", "workDir": str(work_dir), "participantIds": [agents[0]["id"], agents[1]["id"]]},
    ).json()["data"]

    async def fake_plan_job(job, db):
        agent = job["agents"][0]
        return {
            "status": "ready",
            "reasoningSummary": "preview artifact regression",
            "tasks": [
                {
                    "id": "task-1",
                    "title": "生成天气小程序",
                    "agentId": agent.id,
                    "agentName": agent.name,
                    "objective": "生成可预览天气小程序",
                    "instruction": "请实现一个天气小程序，右侧需要预览",
                    "acceptanceCriteria": ["创建 index.html 并可预览"],
                    "constraints": [],
                    "accessMode": "write",
                    "dependsOn": [],
                    "priority": 100,
                    "riskHints": {},
                }
            ],
        }

    monkeypatch.setattr(ws_handlers, "plan_job", fake_plan_job)

    with client.websocket_connect(f"/ws/{conversation['id']}") as websocket:
        websocket.send_json({"type": "send_message", "data": {"content": "请实现一个天气小程序，右侧需要预览", "mentions": []}})
        events = []
        for _ in range(40):
            event = websocket.receive_json()
            events.append(event)
            if event["type"] == "orchestrator_status" and event["data"]["status"] == "completed":
                break

    text_events = [event for event in events if event["type"] == "text_delta"]
    assert text_events
    assert all("sessionID" not in event["data"]["delta"] for event in text_events)
    artifacts = [event["data"]["artifact"] for event in events if event["type"] == "artifact"]
    webpage_artifacts = [artifact for artifact in artifacts if artifact["type"] == "webpage"]
    assert webpage_artifacts
    assert webpage_artifacts[0]["title"] == "index.html"
    assert webpage_artifacts[0]["previewUrl"] == f"/preview/{conversation['id']}/index.html"
    assert client.get(webpage_artifacts[0]["previewUrl"]).status_code == 200
    shutil.rmtree(work_dir)


def test_websocket_reconnect_restores_persisted_snapshot_when_memory_cache_is_empty(client, create_agent):
    agent = create_agent()
    conversation = client.post(
        "/api/v1/conversations",
        json={"type": "single", "workDir": "", "participantIds": [agent["id"]]},
    ).json()["data"]

    with client.websocket_connect(f"/ws/{conversation['id']}") as websocket:
        websocket.send_json({"type": "send_message", "data": {"content": "persist status", "mentions": []}})
        while True:
            event = websocket.receive_json()
            if event["type"] == "orchestrator_status" and event["data"]["status"] == "completed":
                completed = event
                break

    ws_handlers.manager.latest_snapshots.pop(conversation["id"], None)
    with client.websocket_connect(f"/ws/{conversation['id']}") as websocket:
        restored = websocket.receive_json()

    assert restored == completed


def test_websocket_queues_second_message_until_active_run_finishes(client, monkeypatch, create_agent):
    class SlowAdapter:
        def __init__(self, response_delay=0):
            pass

        async def run_task(self, work_dir, instruction, context):
            await asyncio.sleep(0.03)
            yield AgentEvent(type="text_delta", content=instruction)
            yield AgentEvent(type="done")

    monkeypatch.setattr(ws_handlers, "MockAdapter", SlowAdapter)
    agent = create_agent()
    conversation = client.post(
        "/api/v1/conversations",
        json={"type": "single", "workDir": "", "participantIds": [agent["id"]]},
    ).json()["data"]

    with client.websocket_connect(f"/ws/{conversation['id']}") as websocket:
        websocket.send_json({"type": "send_message", "data": {"content": "first", "mentions": []}})
        websocket.send_json({"type": "send_message", "data": {"content": "second", "mentions": []}})
        completed = []
        queued = []
        for _ in range(40):
            event = websocket.receive_json()
            if event["type"] == "orchestrator_status":
                if event["data"]["status"] == "queued":
                    queued.append(event["data"]["runId"])
                if event["data"]["status"] == "completed":
                    completed.append(event["data"]["runId"])
                    if len(completed) == 2:
                        break

    assert len(set(queued)) == 2
    assert completed == list(dict.fromkeys(queued))


def test_websocket_executes_same_batch_in_parallel_with_handoff_context(client, monkeypatch, create_agent):
    active = 0
    max_active = 0
    contexts = []
    work_dir = WORKSPACE_ROOT / f"pytest-parallel-handoff-{uuid.uuid4()}"
    work_dir.mkdir(parents=True)

    class ObservingAdapter:
        def __init__(self, response_delay=0):
            pass

        async def run_task(self, work_dir, instruction, context):
            nonlocal active, max_active
            contexts.append(context)
            active += 1
            max_active = max(max_active, active)
            await asyncio.sleep(0.03)
            active -= 1
            yield AgentEvent(type="done")

    monkeypatch.setattr(ws_handlers, "MockAdapter", ObservingAdapter)
    agents = [create_agent(), create_agent()]
    conversation = client.post(
        "/api/v1/conversations",
        json={"type": "group", "workDir": str(work_dir), "participantIds": [agents[0]["id"], agents[1]["id"]]},
    ).json()["data"]

    with client.websocket_connect(f"/ws/{conversation['id']}") as websocket:
        websocket.send_json({"type": "send_message", "data": {"content": "build and review", "mentions": []}})
        while True:
            event = websocket.receive_json()
            if event["type"] == "orchestrator_status" and event["data"]["status"] == "completed":
                break

    assert max_active == 2
    assert len(contexts) == 2
    assert {context["workspace"]["accessMode"] for context in contexts} == {"read", "write"}
    assert all(context["runId"] and context["taskId"] and context["manifest"] for context in contexts)
    shutil.rmtree(work_dir)


def test_stop_generation_cancels_active_run(client, monkeypatch, create_agent):
    class SlowAdapter:
        def __init__(self, response_delay=0):
            pass

        async def run_task(self, work_dir, instruction, context):
            await asyncio.Event().wait()
            yield AgentEvent(type="done")

    monkeypatch.setattr(ws_handlers, "MockAdapter", SlowAdapter)
    agent = create_agent()
    conversation = client.post(
        "/api/v1/conversations",
        json={"type": "single", "workDir": "", "participantIds": [agent["id"]]},
    ).json()["data"]

    with client.websocket_connect(f"/ws/{conversation['id']}") as websocket:
        websocket.send_json({"type": "send_message", "data": {"content": "cancel me", "mentions": []}})
        while True:
            event = websocket.receive_json()
            if event["type"] == "orchestrator_status" and event["data"]["status"] == "executing":
                websocket.send_json({"type": "stop_generation", "data": {"messageId": "unused"}})
                break
        while True:
            event = websocket.receive_json()
            if event["type"] == "orchestrator_status" and event["data"]["status"] == "cancelled":
                break

    assert event["data"]["status"] == "cancelled"


def test_write_task_downgraded_to_text_only_llm_fails_with_visible_warning(client, monkeypatch):
    work_dir = WORKSPACE_ROOT / f"pytest-write-downgrade-{uuid.uuid4()}"
    work_dir.mkdir(parents=True)

    class UnhealthyCLI:
        async def health_check(self):
            return False

        async def run_task(self, work_dir, instruction, context):
            yield AgentEvent(type="done")

    class TextOnlyLLM:
        async def health_check(self):
            return True

        async def run_task(self, work_dir, instruction, context):
            yield AgentEvent(type="text_delta", content="claimed write")
            yield AgentEvent(type="done")

    async def resolve_agents(db, conversation, mentions):
        return [SimpleNamespace(id=conversation.participant_ids[0], name="Builder", platform_id="codex")]

    async def fake_plan_job(job, db):
        agent = job["agents"][0]
        return {
            "status": "ready",
            "reasoningSummary": "write downgrade",
            "tasks": [
                {
                    "id": "task-1",
                    "title": "Build",
                    "agentId": agent.id,
                    "agentName": agent.name,
                    "objective": "Build",
                    "instruction": "Build",
                    "acceptanceCriteria": ["Create file"],
                    "constraints": [],
                    "accessMode": "write",
                    "dependsOn": [],
                    "priority": 100,
                    "riskHints": {},
                }
            ],
        }

    monkeypatch.setattr(ws_handlers, "resolve_dispatch_agents", resolve_agents)
    monkeypatch.setattr(ws_handlers, "plan_job", fake_plan_job)
    monkeypatch.setattr(
        ws_handlers,
        "agent_manager",
        AgentManagerService(factories={"codex": UnhealthyCLI, "llm": TextOnlyLLM, "mock": TextOnlyLLM}),
    )
    agent = client.get("/api/v1/agents").json()["data"][0]
    conversation = client.post(
        "/api/v1/conversations",
        json={"type": "single", "workDir": str(work_dir), "participantIds": [agent["id"]]},
    ).json()["data"]

    with client.websocket_connect(f"/ws/{conversation['id']}") as websocket:
        websocket.send_json({"type": "send_message", "data": {"content": "build", "mentions": []}})
        while True:
            event = websocket.receive_json()
            if event["type"] == "orchestrator_status" and event["data"]["status"] == "completed":
                snapshot = event["data"]
                break

    assert snapshot["tasks"][0]["status"] == "failed"
    assert "no workspace changes" in snapshot["tasks"][0]["result"]
    assert "Adapter downgraded to llm" in snapshot["warnings"]
    shutil.rmtree(work_dir)


def test_downstream_handoff_receives_prior_batch_audit_and_real_batch_id(client, monkeypatch, create_agent):
    contexts = []
    work_dir = WORKSPACE_ROOT / f"pytest-handoff-audit-{uuid.uuid4()}"
    work_dir.mkdir(parents=True)

    class AuditingAdapter:
        def __init__(self, response_delay=0):
            pass

        async def run_task(self, work_dir, instruction, context):
            contexts.append(context)
            if context["taskId"] == "task-1":
                Path(work_dir, "created.txt").write_text("created", encoding="utf-8")
            yield AgentEvent(type="done")

    async def fake_plan_job(job, db):
        agents = job["agents"]
        return {
            "status": "ready",
            "reasoningSummary": "sequential audit",
            "tasks": [
                {
                    "id": "task-1",
                    "title": "Build",
                    "agentId": agents[0].id,
                    "agentName": agents[0].name,
                    "objective": "Build",
                    "instruction": "Build",
                    "acceptanceCriteria": ["Create a file"],
                    "constraints": [],
                    "accessMode": "write",
                    "dependsOn": [],
                    "priority": 100,
                    "riskHints": {},
                },
                {
                    "id": "task-2",
                    "title": "Review",
                    "agentId": agents[1].id,
                    "agentName": agents[1].name,
                    "objective": "Review",
                    "instruction": "Review",
                    "acceptanceCriteria": ["Inspect changes"],
                    "constraints": [],
                    "accessMode": "read",
                    "dependsOn": ["task-1"],
                    "priority": 90,
                    "riskHints": {},
                },
            ],
        }

    monkeypatch.setattr(ws_handlers, "MockAdapter", AuditingAdapter)
    monkeypatch.setattr(ws_handlers, "plan_job", fake_plan_job)
    agents = [create_agent(), create_agent()]
    conversation = client.post(
        "/api/v1/conversations",
        json={"type": "group", "workDir": str(work_dir), "participantIds": [agents[0]["id"], agents[1]["id"]]},
    ).json()["data"]

    with client.websocket_connect(f"/ws/{conversation['id']}") as websocket:
        websocket.send_json({"type": "send_message", "data": {"content": "build and review", "mentions": []}})
        while True:
            event = websocket.receive_json()
            if event["type"] == "orchestrator_status" and event["data"]["status"] == "completed":
                break

    assert [context["batchId"] for context in contexts] == ["batch-1", "batch-2"]
    assert contexts[1]["navigationHints"]["changedFiles"] == ["created.txt"]
    assert contexts[1]["collaboration"]["dependencyResults"][0]["filesChanged"] == ["created.txt"]
    shutil.rmtree(work_dir)


def test_read_task_retries_safe_execution_fallback_and_surfaces_warning(client, monkeypatch):
    class FailingAdapter:
        async def health_check(self):
            return True

        async def run_task(self, work_dir, instruction, context):
            yield AgentEvent(type="error", content="cli crashed")
            yield AgentEvent(type="done")

    class HealthyFallback:
        async def health_check(self):
            return True

        async def run_task(self, work_dir, instruction, context):
            yield AgentEvent(type="text_delta", content="fallback result")
            yield AgentEvent(type="done")

    async def resolve_agents(db, conversation, mentions):
        return [SimpleNamespace(id=conversation.participant_ids[0], name="Builder", platform_id="codex")]

    async def fake_plan_job(job, db):
        agent = job["agents"][0]
        return {
            "status": "ready",
            "reasoningSummary": "read fallback",
            "tasks": [
                {
                    "id": "task-1",
                    "title": "Review",
                    "agentId": agent.id,
                    "agentName": agent.name,
                    "objective": "Review",
                    "instruction": "Review",
                    "acceptanceCriteria": ["Return review"],
                    "constraints": [],
                    "accessMode": "read",
                    "dependsOn": [],
                    "priority": 100,
                    "riskHints": {},
                }
            ],
        }

    monkeypatch.setattr(ws_handlers, "resolve_dispatch_agents", resolve_agents)
    monkeypatch.setattr(ws_handlers, "plan_job", fake_plan_job)
    monkeypatch.setattr(
        ws_handlers,
        "agent_manager",
        AgentManagerService(
            factories={
                "codex": FailingAdapter,
                "llm": HealthyFallback,
                "mock": HealthyFallback,
            }
        ),
    )
    agent = client.get("/api/v1/agents").json()["data"][0]
    conversation = client.post(
        "/api/v1/conversations",
        json={"type": "single", "workDir": "", "participantIds": [agent["id"]]},
    ).json()["data"]

    with client.websocket_connect(f"/ws/{conversation['id']}") as websocket:
        websocket.send_json({"type": "send_message", "data": {"content": "review", "mentions": []}})
        while True:
            event = websocket.receive_json()
            if event["type"] == "orchestrator_status" and event["data"]["status"] == "completed":
                snapshot = event["data"]
                break

    assert snapshot["tasks"][0]["status"] == "completed"
    assert "Adapter codex failed during execution; retried with llm" in snapshot["warnings"]
