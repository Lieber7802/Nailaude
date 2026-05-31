from types import SimpleNamespace
from datetime import datetime, timezone
import shutil
import uuid

import pytest

from app.schemas.conversation import WORKSPACE_ROOT
from app.schemas.orchestrator import ReadyPlannerResult
from app.services.orchestrator import OrchestratorService
import app.ws.handlers as ws_handlers


def _create_conversation(client, work_dir=""):
    agents = client.get("/api/v1/agents").json()["data"]
    conversation = client.post(
        "/api/v1/conversations",
        json={"type": "single", "workDir": str(work_dir), "participantIds": [agents[0]["id"]]},
    ).json()["data"]
    return conversation, agents


def test_clarification_response_requeues_and_resumes_planning(client, monkeypatch):
    conversation, agents = _create_conversation(client)
    calls = []

    async def fake_plan_job(job, db):
        calls.append(list(job.get("clarification_answers") or []))
        if len(calls) == 1:
            return {
                "status": "needs_clarification",
                "questions": [
                    {
                        "id": "scope",
                        "question": "Which scope?",
                        "reason": "The requested scope is ambiguous.",
                        "options": [{"id": "minimal", "label": "Minimal", "recommended": True}],
                        "allowCustomInput": True,
                    }
                ],
            }
        return await OrchestratorService().build_mock_planner_result(
            job["conversation"], job["content"], job["mentions"], job["agents"]
        )

    monkeypatch.setattr(ws_handlers, "plan_job", fake_plan_job)

    with client.websocket_connect(f"/ws/{conversation['id']}") as websocket:
        websocket.send_json({"type": "send_message", "data": {"content": "build", "mentions": []}})
        while True:
            event = websocket.receive_json()
            if event["type"] == "orchestrator_input_required":
                run_id = event["data"]["runId"]
                assert event["data"]["result"]["status"] == "needs_clarification"
                break
        websocket.send_json(
            {"type": "orchestrator_input_response", "data": {"runId": run_id, "answers": {"scope": "minimal"}}}
        )
        while True:
            event = websocket.receive_json()
            if event["type"] == "orchestrator_status" and event["data"]["status"] == "completed":
                break

    assert calls == [[], [{"scope": "minimal"}]]


def test_clarification_response_requires_all_answers_atomically(client, monkeypatch):
    conversation, _agents = _create_conversation(client)
    calls = []

    async def fake_plan_job(job, db):
        calls.append(list(job.get("clarification_answers") or []))
        if len(calls) == 1:
            return {
                "status": "needs_clarification",
                "questions": [
                    {
                        "id": "scope",
                        "question": "Which scope?",
                        "reason": "Scope is ambiguous.",
                        "options": [{"id": "minimal", "label": "Minimal", "recommended": True}],
                        "allowCustomInput": True,
                    },
                    {
                        "id": "storage",
                        "question": "Which storage?",
                        "reason": "Storage is ambiguous.",
                        "options": [{"id": "memory", "label": "Memory", "recommended": True}],
                        "allowCustomInput": True,
                    },
                ],
            }
        return await OrchestratorService().build_mock_planner_result(
            job["conversation"], job["content"], job["mentions"], job["agents"]
        )

    monkeypatch.setattr(ws_handlers, "plan_job", fake_plan_job)

    with client.websocket_connect(f"/ws/{conversation['id']}") as websocket:
        websocket.send_json({"type": "send_message", "data": {"content": "build", "mentions": []}})
        while True:
            event = websocket.receive_json()
            if event["type"] == "orchestrator_input_required":
                run_id = event["data"]["runId"]
                break
        websocket.send_json(
            {"type": "orchestrator_input_response", "data": {"runId": run_id, "answers": {"scope": "minimal"}}}
        )
        error = websocket.receive_json()
        assert error["type"] == "error"
        assert "all clarification questions" in error["data"]["error"]
        websocket.send_json(
            {
                "type": "orchestrator_input_response",
                "data": {"runId": run_id, "answers": {"scope": "minimal", "storage": "memory"}},
            }
        )
        while True:
            event = websocket.receive_json()
            if event["type"] == "orchestrator_status" and event["data"]["status"] == "completed":
                break

    assert calls == [[], [{"scope": "minimal", "storage": "memory"}]]


def test_cannot_plan_fails_run_without_publishing_input_request(client, monkeypatch):
    conversation, _agents = _create_conversation(client)

    async def fake_plan_job(job, db):
        return {"status": "cannot_plan", "reason": "Outside workspace", "recoverable": True}

    monkeypatch.setattr(ws_handlers, "plan_job", fake_plan_job)

    with client.websocket_connect(f"/ws/{conversation['id']}") as websocket:
        websocket.send_json({"type": "send_message", "data": {"content": "build", "mentions": []}})
        events = []
        while True:
            event = websocket.receive_json()
            events.append(event)
            if event["type"] == "error":
                break

    assert event["data"] == {"error": "Outside workspace", "recoverable": True}
    assert "orchestrator_input_required" not in [item["type"] for item in events]
    failed = [item for item in events if item["type"] == "orchestrator_status"][-1]
    assert failed["data"]["status"] == "failed"


def test_elevated_write_approval_resumes_without_replanning(client, monkeypatch):
    work_dir = WORKSPACE_ROOT / f"pytest-approval-{uuid.uuid4()}"
    work_dir.mkdir(parents=True)
    conversation, _agents = _create_conversation(client, work_dir)
    calls = 0

    async def fake_plan_job(job, db):
        nonlocal calls
        calls += 1
        result = await OrchestratorService().build_mock_planner_result(
            job["conversation"], job["content"], job["mentions"], job["agents"]
        )
        result["tasks"][0]["riskHints"]["mayTouchConfigFiles"] = True
        return result

    monkeypatch.setattr(ws_handlers, "plan_job", fake_plan_job)

    with client.websocket_connect(f"/ws/{conversation['id']}") as websocket:
        websocket.send_json({"type": "send_message", "data": {"content": "update config", "mentions": []}})
        while True:
            event = websocket.receive_json()
            if event["type"] == "orchestrator_approval_required":
                run_id = event["data"]["runId"]
                assert event["data"]["tasks"][0]["riskHints"]["mayTouchConfigFiles"] is True
                break
        websocket.send_json({"type": "orchestrator_approval_response", "data": {"runId": run_id, "approved": True}})
        while True:
            event = websocket.receive_json()
            if event["type"] == "orchestrator_status" and event["data"]["status"] == "completed":
                break

    assert calls == 1
    shutil.rmtree(work_dir)


def test_cross_conversation_input_response_does_not_consume_paused_job(client, monkeypatch):
    first, _agents = _create_conversation(client)
    second, _agents = _create_conversation(client)

    async def fake_plan_job(job, db):
        if not job.get("clarification_answers"):
            return {
                "status": "needs_clarification",
                "questions": [
                    {
                        "id": "scope",
                        "question": "Which scope?",
                        "reason": "Scope is ambiguous.",
                        "options": [{"id": "minimal", "label": "Minimal", "recommended": True}],
                        "allowCustomInput": True,
                    }
                ],
            }
        return await OrchestratorService().build_mock_planner_result(
            job["conversation"], job["content"], job["mentions"], job["agents"]
        )

    monkeypatch.setattr(ws_handlers, "plan_job", fake_plan_job)

    with client.websocket_connect(f"/ws/{first['id']}") as first_ws:
        first_ws.send_json({"type": "send_message", "data": {"content": "build", "mentions": []}})
        while True:
            event = first_ws.receive_json()
            if event["type"] == "orchestrator_input_required":
                run_id = event["data"]["runId"]
                break
        with client.websocket_connect(f"/ws/{second['id']}") as second_ws:
            second_ws.send_json(
                {"type": "orchestrator_input_response", "data": {"runId": run_id, "answers": {"scope": "minimal"}}}
            )
            error = second_ws.receive_json()
        assert error["type"] == "error"
        first_ws.send_json(
            {"type": "orchestrator_input_response", "data": {"runId": run_id, "answers": {"scope": "minimal"}}}
        )
        while True:
            event = first_ws.receive_json()
            if event["type"] == "orchestrator_status" and event["data"]["status"] == "completed":
                break


def test_cross_conversation_approval_response_does_not_consume_paused_job(client, monkeypatch):
    work_dir = WORKSPACE_ROOT / f"pytest-cross-approval-{uuid.uuid4()}"
    work_dir.mkdir(parents=True)
    first, _agents = _create_conversation(client, work_dir)
    second, _agents = _create_conversation(client)

    async def fake_plan_job(job, db):
        result = await OrchestratorService().build_mock_planner_result(
            job["conversation"], job["content"], job["mentions"], job["agents"]
        )
        result["tasks"][0]["riskHints"]["mayTouchConfigFiles"] = True
        return result

    monkeypatch.setattr(ws_handlers, "plan_job", fake_plan_job)

    with client.websocket_connect(f"/ws/{first['id']}") as first_ws:
        first_ws.send_json({"type": "send_message", "data": {"content": "build", "mentions": []}})
        while True:
            event = first_ws.receive_json()
            if event["type"] == "orchestrator_approval_required":
                run_id = event["data"]["runId"]
                break
        with client.websocket_connect(f"/ws/{second['id']}") as second_ws:
            second_ws.send_json({"type": "orchestrator_approval_response", "data": {"runId": run_id, "approved": True}})
            error = second_ws.receive_json()
        assert error["type"] == "error"
        first_ws.send_json({"type": "orchestrator_approval_response", "data": {"runId": run_id, "approved": True}})
        while True:
            event = first_ws.receive_json()
            if event["type"] == "orchestrator_status" and event["data"]["status"] == "completed":
                break
    shutil.rmtree(work_dir)


@pytest.mark.asyncio
async def test_non_mock_job_uses_deepseek_planner_wrapper(monkeypatch):
    agent = SimpleNamespace(
        id="agent-1",
        name="Builder",
        description="Builds features",
        capabilities=["coding"],
        platform_id="llm",
    )
    conversation = SimpleNamespace(id="conversation-1", participant_ids=["agent-1"])
    captured = {}
    updated_at = datetime.now(timezone.utc)
    project_state = SimpleNamespace(
        conversation_id=conversation.id,
        version=2,
        workspace={},
        tech_stack=[],
        file_tree={"paths": ["src/app.py"]},
        git={},
        progress_summary="Current project summary",
        recent_changes=[],
        warnings=[],
        updated_at=updated_at,
    )
    team_board = SimpleNamespace(
        conversation_id=conversation.id,
        version=3,
        team_members=[],
        decisions=[],
        code_standards=[],
        open_questions=[],
        progress={},
        recent_notes=[],
        updated_at=updated_at,
    )

    class Scalars:
        def __init__(self, items):
            self.items = items

        def all(self):
            return self.items

    class FakeDB:
        def __init__(self):
            self.calls = 0

        async def scalars(self, query):
            self.calls += 1
            if self.calls <= 2:
                return Scalars([agent])
            return Scalars([SimpleNamespace(role="user", content="Earlier request")])

    class FakePlanner:
        async def plan(self, context, participant_ids):
            captured["context"] = context
            captured["participant_ids"] = participant_ids
            return ReadyPlannerResult(
                status="ready",
                tasks=[
                    {
                        "id": "task-1",
                        "title": "Build",
                        "agentId": "agent-1",
                        "objective": "Build",
                        "instruction": "Build",
                        "acceptanceCriteria": ["Done"],
                        "accessMode": "read",
                    }
                ],
            )

    class FakeProjectStateService:
        def __init__(self, db):
            pass

        async def get_state(self, conversation_id):
            return project_state

    class FakeTeamProtocolService:
        def __init__(self, db):
            pass

        async def get_team_board(self, conversation_id):
            return team_board

    monkeypatch.setattr(ws_handlers, "OrchestratorPlanner", FakePlanner)
    monkeypatch.setattr(ws_handlers, "ProjectStateService", FakeProjectStateService)
    monkeypatch.setattr(ws_handlers, "TeamProtocolService", FakeTeamProtocolService)

    result = await ws_handlers.plan_job(
        {
            "conversation": conversation,
            "content": "Build",
            "mentions": [],
            "agents": [agent],
            "clarification_answers": [],
        },
        FakeDB(),
    )

    assert result["status"] == "ready"
    assert captured["participant_ids"] == {"agent-1"}
    assert captured["context"]["participants"][0]["capabilities"] == ["coding"]
    assert captured["context"]["projectPlanningSummary"]["progressSummary"] == "Current project summary"
    assert captured["context"]["teamBoardSummary"]["version"] == 3
    assert captured["context"]["fileTreeSummary"] == ["src/app.py"]
    assert captured["context"]["recentConversationSummary"] == [{"role": "user", "content": "Earlier request"}]
