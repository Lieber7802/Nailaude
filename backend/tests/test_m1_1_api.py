def assert_api_response(payload, success=True):
    assert payload["success"] is success
    assert "data" in payload
    assert "error" in payload
    assert "timestamp" in payload


def test_agents_are_seeded_and_return_camel_case_fields(client):
    response = client.get("/api/v1/agents")

    assert response.status_code == 200
    payload = response.json()
    assert_api_response(payload)
    names = {agent["name"] for agent in payload["data"]}
    assert {"代码工匠", "审查大师", "文档专家"}.issubset(names)
    first_agent = payload["data"][0]
    assert "platformId" in first_agent
    assert "isBuiltin" in first_agent
    assert "createdAt" in first_agent
    assert "platform_id" not in first_agent


def test_builtin_agents_are_backed_by_opencode(client):
    response = client.get("/api/v1/agents")

    assert response.status_code == 200
    payload = response.json()
    agents_by_name = {agent["name"]: agent for agent in payload["data"]}
    for name in ("代码工匠", "审查大师", "文档专家"):
        assert agents_by_name[name]["platformId"] == "opencode"


def test_platforms_refresh_cli_statuses_from_installed_binaries(client, monkeypatch):
    from app.services import platform_status

    def fake_which(binary_path):
        return f"/usr/local/bin/{binary_path}" if binary_path in {"codex", "opencode"} else None

    async def fake_check_health(self, platform_id):
        return platform_id in {"codex", "opencode", "mock"}

    monkeypatch.setattr(platform_status.shutil, "which", fake_which)
    monkeypatch.setattr(platform_status.AgentManagerService, "check_health", fake_check_health)

    response = client.get("/api/v1/platforms")

    assert response.status_code == 200
    payload = response.json()
    assert_api_response(payload)
    platforms_by_id = {platform["id"]: platform for platform in payload["data"]}
    assert platforms_by_id["codex"]["status"] == "available"
    assert platforms_by_id["opencode"]["status"] == "available"
    assert platforms_by_id["mock"]["status"] == "available"


def test_create_custom_agent_persists_and_lists(client):
    create_response = client.post(
        "/api/v1/agents",
        json={
            "name": "产品经理",
            "avatar": "P",
            "description": "将用户需求整理成结构化 PRD 和验收标准。",
            "capabilities": ["产品", "需求分析", "文档"],
            "systemInstruction": "你是资深产品经理，负责澄清需求并输出可执行规格。",
            "platformId": "mock",
        },
    )

    assert create_response.status_code == 200
    created = create_response.json()
    assert_api_response(created)
    assert created["data"]["name"] == "产品经理"
    assert created["data"]["description"] == "将用户需求整理成结构化 PRD 和验收标准。"
    assert created["data"]["capabilities"] == ["产品", "需求分析", "文档"]
    assert created["data"]["systemInstruction"] == "你是资深产品经理，负责澄清需求并输出可执行规格。"
    assert created["data"]["platformId"] == "mock"
    assert created["data"]["isBuiltin"] is False

    list_response = client.get("/api/v1/agents")
    assert list_response.status_code == 200
    listed = list_response.json()
    custom_agents = [agent for agent in listed["data"] if agent["id"] == created["data"]["id"]]
    assert len(custom_agents) == 1
    assert custom_agents[0]["isBuiltin"] is False


def test_create_and_list_group_conversation(client):
    agent_id = client.get("/api/v1/agents").json()["data"][0]["id"]

    create_response = client.post(
        "/api/v1/conversations",
        json={
            "title": "Todo App 开发",
            "type": "group",
            "workDir": "D:/AgentHub/workspaces/todo-app",
            "participantIds": [agent_id],
        },
    )

    assert create_response.status_code == 200
    created = create_response.json()
    assert_api_response(created)
    assert created["data"]["title"] == "Todo App 开发"
    assert created["data"]["workDir"] == "D:/AgentHub/workspaces/todo-app"
    assert created["data"]["participantIds"] == [agent_id]

    list_response = client.get("/api/v1/conversations?page=1&pageSize=10&search=Todo")
    assert list_response.status_code == 200
    listed = list_response.json()
    assert_api_response(listed)
    assert listed["data"]["total"] == 1
    assert listed["data"]["items"][0]["id"] == created["data"]["id"]

    detail_response = client.get(f"/api/v1/conversations/{created['data']['id']}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["data"]["id"] == created["data"]["id"]


def test_create_conversation_creates_relative_workspace_directory(client):
    from pathlib import Path
    from uuid import uuid4
    import shutil

    from app.schemas.conversation import WORKSPACE_ROOT

    agent_id = client.get("/api/v1/agents").json()["data"][0]["id"]
    workspace_name = f"pytest-create-workspace-{uuid4()}"
    work_dir = WORKSPACE_ROOT / workspace_name
    try:
        response = client.post(
            "/api/v1/conversations",
            json={
                "title": "Workspace Create",
                "type": "single",
                "workDir": f"workspaces/{workspace_name}",
                "participantIds": [agent_id],
            },
        )

        assert response.status_code == 200
        assert Path(work_dir).is_dir()
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def test_rest_message_fallback_persists_user_message_only(client):
    agent_id = client.get("/api/v1/agents").json()["data"][0]["id"]
    conversation = client.post(
        "/api/v1/conversations",
        json={
            "title": "Message Test",
            "type": "single",
            "workDir": "D:/AgentHub/workspaces/message-test",
            "participantIds": [agent_id],
        },
    ).json()["data"]

    send_response = client.post(
        f"/api/v1/conversations/{conversation['id']}/messages",
        json={
            "content": "@代码工匠 帮我生成登录页",
            "mentions": [{"agentId": agent_id, "agentName": "代码工匠"}],
            "parentMessageId": None,
        },
    )

    assert send_response.status_code == 200
    sent = send_response.json()
    assert_api_response(sent)
    assert sent["data"]["role"] == "user"
    assert sent["data"]["agentId"] is None
    assert sent["data"]["content"] == "@代码工匠 帮我生成登录页"
    assert sent["data"]["artifacts"] == []

    list_response = client.get(f"/api/v1/conversations/{conversation['id']}/messages")
    listed = list_response.json()
    assert listed["data"]["total"] == 1
    assert listed["data"]["items"][0]["id"] == sent["data"]["id"]


def test_missing_conversation_errors_use_api_response(client):
    response = client.get("/api/v1/conversations/missing-conversation")

    assert response.status_code == 404
    payload = response.json()
    assert_api_response(payload, success=False)
    assert payload["data"] is None
    assert payload["error"] == "Conversation not found"

    send_response = client.post(
        "/api/v1/conversations/missing-conversation/messages",
        json={"content": "hello", "mentions": []},
    )
    assert send_response.status_code == 404
    assert send_response.json()["error"] == "Conversation not found"


def test_validation_errors_use_api_response_and_reject_unsafe_workdir(client):
    response = client.post(
        "/api/v1/conversations",
        json={
            "title": "Unsafe Workspace",
            "type": "single",
            "workDir": "../outside",
            "participantIds": [],
        },
    )

    assert response.status_code == 422
    payload = response.json()
    assert_api_response(payload, success=False)
    assert payload["data"] is None
    assert "workDir" in payload["error"]

    invalid_type_response = client.post(
        "/api/v1/conversations",
        json={
            "title": "Bad Type",
            "type": "channel",
            "workDir": "workspaces/bad-type",
            "participantIds": [],
        },
    )
    assert invalid_type_response.status_code == 422
    invalid_type = invalid_type_response.json()
    assert_api_response(invalid_type, success=False)
    assert "type" in invalid_type["error"]
