from app.ws.manager import manager


def test_websocket_send_message_streams_mock_events_and_persists_results(client, create_agent):
    agent = create_agent(name="代码工匠 Mock")
    agent_id = agent["id"]
    conversation = client.post(
        "/api/v1/conversations",
        json={
            "title": "WS Mock Test",
            "type": "single",
            "workDir": "D:/AgentHub/workspaces/ws-mock-test",
            "participantIds": [agent_id],
        },
    ).json()["data"]

    with client.websocket_connect(f"/ws/{conversation['id']}") as websocket:
        websocket.send_json(
            {
                "type": "send_message",
                "data": {
                    "content": "@代码工匠 生成一个登录页",
                    "mentions": [{"agentId": agent_id, "agentName": agent["name"]}],
                    "parentMessageId": None,
                    "clientMessageId": "client-1",
                },
            }
        )
        events = []
        first_event = websocket.receive_json()
        events.append(first_event)
        assert first_event["type"] == "user_message"
        assert first_event["data"]["clientMessageId"] == "client-1"

        for _ in range(24):
            event = websocket.receive_json()
            events.append(event)
            if event["type"] == "orchestrator_status" and event["data"]["status"] == "completed":
                break

    event_types = [event["type"] for event in events]
    assert "agent_thinking" in event_types
    assert "text_delta" in event_types
    assert "artifact" in event_types
    assert "team_activity" in event_types
    assert "message_done" in event_types
    assert events[-1]["data"]["status"] == "completed"

    artifact_event = next(event for event in events if event["type"] == "artifact")
    artifact = artifact_event["data"]["artifact"]
    assert artifact["type"] == "webpage"
    assert artifact["files"][0]["name"] == "index.html"
    assert artifact["messageId"] == artifact_event["data"]["messageId"]

    messages = client.get(f"/api/v1/conversations/{conversation['id']}/messages").json()["data"]["items"]
    assert [message["role"] for message in messages] == ["user", "agent"]
    assert messages[0]["content"] == "@代码工匠 生成一个登录页"
    assert "Mock 已生成" in messages[1]["content"]
    assert messages[1]["agentName"] == agent["name"]
    assert len(messages[1]["artifacts"]) == 1
    assert messages[1]["artifacts"][0]["title"] == "index.html"

    artifacts = client.get(f"/api/v1/artifacts?message_id={messages[1]['id']}").json()["data"]
    assert len(artifacts) == 1
    assert artifacts[0]["title"] == "index.html"


def test_websocket_missing_conversation_returns_error(client):
    with client.websocket_connect("/ws/missing-conversation") as websocket:
        websocket.send_json({"type": "send_message", "data": {"content": "hello", "mentions": []}})
        event = websocket.receive_json()

    assert event["type"] == "error"
    assert event["data"]["error"] == "Conversation not found"
    assert event["data"]["recoverable"] is False


def test_websocket_malformed_json_returns_error_and_cleans_connection(client, create_agent):
    agent_id = create_agent()["id"]
    conversation = client.post(
        "/api/v1/conversations",
        json={
            "title": "Malformed WS",
            "type": "single",
            "workDir": "D:/AgentHub/workspaces/malformed-ws",
            "participantIds": [agent_id],
        },
    ).json()["data"]

    with client.websocket_connect(f"/ws/{conversation['id']}") as websocket:
        websocket.send_text("{not-json")
        event = websocket.receive_json()
        assert event["type"] == "error"
        assert event["data"]["recoverable"] is True
        assert "Invalid JSON" in event["data"]["error"]

    assert conversation["id"] not in manager.active_connections
