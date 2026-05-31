import pytest

from app.adapters.base import AgentEvent
from app.services.orchestrator import OrchestratorService
import app.ws.handlers as ws_handlers
from app.ws.manager import manager


def _agent_ids(client):
    agents = client.get("/api/v1/agents").json()["data"]
    return agents, [agent["id"] for agent in agents]


def test_conversation_list_returns_last_message_and_searches_it(client):
    agents, agent_ids = _agent_ids(client)
    conversation = client.post(
        "/api/v1/conversations",
        json={
            "title": "M2 Search Demo",
            "type": "group",
            "workDir": "workspaces/m2-search-demo",
            "participantIds": agent_ids[:2],
        },
    ).json()["data"]

    client.post(
        f"/api/v1/conversations/{conversation['id']}/messages",
        json={
            "content": f"@{agents[0]['name']} build the shell",
            "mentions": [{"agentId": agents[0]["id"], "agentName": agents[0]["name"]}],
            "parentMessageId": None,
        },
    )

    payload = client.get("/api/v1/conversations?page=1&pageSize=10&search=shell").json()

    assert payload["success"] is True
    assert payload["data"]["total"] == 1
    assert payload["data"]["items"][0]["id"] == conversation["id"]
    assert payload["data"]["items"][0]["lastMessage"] == f"你: @{agents[0]['name']} build the shell"


@pytest.mark.asyncio
async def test_orchestrator_builds_sequential_plan_from_mentions():
    service = OrchestratorService()
    conversation = type(
        "ConversationStub",
        (),
        {"participant_ids": ["agent-1", "agent-2"], "work_dir": "workspaces/demo"},
    )()
    agents = [
        type("AgentStub", (), {"id": "agent-1", "name": "代码工匠"})(),
        type("AgentStub", (), {"id": "agent-2", "name": "审查大师"})(),
    ]

    plan = await service.build_dispatch_plan(
        conversation,
        "请 @代码工匠 生成页面，然后 @审查大师 审查",
        [
            {"agentId": "agent-1", "agentName": "代码工匠"},
            {"agentId": "agent-2", "agentName": "审查大师"},
        ],
        agents,
    )

    assert plan["executionMode"] == "sequential"
    assert [task["agentId"] for task in plan["tasks"]] == ["agent-1", "agent-2"]
    assert [task["status"] for task in plan["tasks"]] == ["pending", "pending"]
    assert plan["tasks"][0]["dependsOn"] is None
    assert plan["tasks"][1]["dependsOn"] == plan["tasks"][0]["id"]
    assert all(task["instruction"] == "请 @代码工匠 生成页面，然后 @审查大师 审查" for task in plan["tasks"])


def test_group_websocket_pushes_orchestrator_status_and_runs_mentioned_agents(client):
    agents, agent_ids = _agent_ids(client)
    conversation = client.post(
        "/api/v1/conversations",
        json={
            "title": "M2 Group Dispatch",
            "type": "group",
            "workDir": "workspaces/m2-group-dispatch",
            "participantIds": agent_ids[:2],
        },
    ).json()["data"]

    with client.websocket_connect(f"/ws/{conversation['id']}") as websocket:
        websocket.send_json(
            {
                "type": "send_message",
                "data": {
                    "content": f"@{agents[0]['name']} 生成页面 @{agents[1]['name']} 审查结果",
                    "mentions": [
                        {"agentId": agents[0]["id"], "agentName": agents[0]["name"]},
                        {"agentId": agents[1]["id"], "agentName": agents[1]["name"]},
                    ],
                    "parentMessageId": None,
                    "clientMessageId": "client-m2",
                },
            }
        )
        events = []
        for _ in range(30):
            event = websocket.receive_json()
            events.append(event)
            if (
                event["type"] == "orchestrator_status"
                and event["data"]["status"] == "summarizing"
                and all(task["status"] == "completed" for task in event["data"]["tasks"])
            ):
                break

    event_types = [event["type"] for event in events]
    assert event_types[0] == "user_message"
    assert event_types.count("orchestrator_status") >= 3
    assert event_types.count("agent_thinking") == 2
    assert event_types.count("message_done") == 2

    status_events = [event for event in events if event["type"] == "orchestrator_status"]
    assert status_events[0]["data"]["status"] == "dispatching"
    assert status_events[-1]["data"]["status"] == "summarizing"
    assert [task["agentName"] for task in status_events[0]["data"]["tasks"]] == [
        agents[0]["name"],
        agents[1]["name"],
    ]

    messages = client.get(f"/api/v1/conversations/{conversation['id']}/messages").json()["data"]["items"]
    assert [message["role"] for message in messages] == ["user", "agent", "agent"]
    assert [message["agentName"] for message in messages[1:]] == [agents[0]["name"], agents[1]["name"]]

    assert conversation["id"] not in manager.active_connections


def test_create_conversation_rejects_empty_participants(client):
    response = client.post(
        "/api/v1/conversations",
        json={
            "title": "No Participants",
            "type": "single",
            "workDir": "workspaces/no-participants",
            "participantIds": [],
        },
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["success"] is False
    assert "participantIds" in payload["error"]


def test_update_conversation_rejects_empty_participants(client):
    _agents, agent_ids = _agent_ids(client)
    conversation = client.post(
        "/api/v1/conversations",
        json={
            "title": "Participant Update",
            "type": "single",
            "workDir": "workspaces/participant-update",
            "participantIds": [agent_ids[0]],
        },
    ).json()["data"]

    response = client.patch(f"/api/v1/conversations/{conversation['id']}", json={"participantIds": []})

    assert response.status_code == 422
    payload = response.json()
    assert payload["success"] is False
    assert "participantIds" in payload["error"]


def test_update_agent_accepts_platform_id_alias(client):
    agents, _ids = _agent_ids(client)
    agent = agents[0]

    response = client.patch(f"/api/v1/agents/{agent['id']}", json={"platformId": "llm"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["platformId"] == "llm"


def test_ws_rejects_mentioned_agent_not_in_conversation(client):
    agents, agent_ids = _agent_ids(client)
    conversation = client.post(
        "/api/v1/conversations",
        json={
            "title": "Participant Boundary",
            "type": "single",
            "workDir": "workspaces/participant-boundary",
            "participantIds": [agent_ids[0]],
        },
    ).json()["data"]

    with client.websocket_connect(f"/ws/{conversation['id']}") as websocket:
        websocket.send_json(
            {
                "type": "send_message",
                "data": {
                    "content": f"@{agents[1]['name']} should not run",
                    "mentions": [{"agentId": agent_ids[1], "agentName": agents[1]["name"]}],
                    "parentMessageId": None,
                },
            }
        )
        event = websocket.receive_json()

    assert event["type"] == "error"
    assert event["data"]["error"] == "Mentioned agent is not part of this conversation"
    messages = client.get(f"/api/v1/conversations/{conversation['id']}/messages").json()["data"]["items"]
    assert messages == []


def test_ws_marks_task_failed_when_adapter_raises(client, monkeypatch):
    class FailingAdapter:
        def __init__(self, response_delay=0):
            self.response_delay = response_delay

        async def run_task(self, work_dir, instruction, context):
            yield AgentEvent(type="text_delta", content="partial")
            raise RuntimeError("adapter exploded")

    monkeypatch.setattr(ws_handlers, "MockAdapter", FailingAdapter)
    agents, agent_ids = _agent_ids(client)
    conversation = client.post(
        "/api/v1/conversations",
        json={
            "title": "Adapter Failure",
            "type": "single",
            "workDir": "workspaces/adapter-failure",
            "participantIds": [agent_ids[0]],
        },
    ).json()["data"]

    with client.websocket_connect(f"/ws/{conversation['id']}") as websocket:
        websocket.send_json(
            {
                "type": "send_message",
                "data": {
                    "content": f"@{agents[0]['name']} trigger failure",
                    "mentions": [{"agentId": agent_ids[0], "agentName": agents[0]["name"]}],
                    "parentMessageId": None,
                },
            }
        )
        events = []
        for _ in range(12):
            event = websocket.receive_json()
            events.append(event)
            if event["type"] == "orchestrator_status" and event["data"]["status"] == "summarizing":
                break

    event_types = [event["type"] for event in events]
    assert "error" in event_types
    final_status = [event for event in events if event["type"] == "orchestrator_status"][-1]
    assert final_status["data"]["tasks"][0]["status"] == "failed"
    assert final_status["data"]["tasks"][0]["result"] == "Mock stream failed: adapter exploded"
