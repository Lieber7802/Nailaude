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
