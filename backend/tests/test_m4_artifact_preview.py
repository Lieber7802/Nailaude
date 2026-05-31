from pathlib import Path
from uuid import uuid4

import pytest

from app.schemas.conversation import WORKSPACE_ROOT
from app.services.file_watcher import FileWatcherService


def test_mock_websocket_generates_webpage_artifact_and_preview_file(client):
    agent_id = client.get("/api/v1/agents").json()["data"][0]["id"]
    work_dir = WORKSPACE_ROOT / f"m4-preview-{uuid4()}"
    work_dir.mkdir(parents=True)
    conversation = client.post(
        "/api/v1/conversations",
        json={
            "title": "M4 Preview",
            "type": "single",
            "workDir": str(work_dir),
            "participantIds": [agent_id],
        },
    ).json()["data"]
    assert conversation is not None

    with client.websocket_connect(f"/ws/{conversation['id']}") as websocket:
        websocket.send_json(
            {
                "type": "send_message",
                "data": {
                    "content": "@代码工匠 生成可预览页面",
                    "mentions": [{"agentId": agent_id, "agentName": "代码工匠"}],
                    "parentMessageId": None,
                },
            }
        )
        events = []
        for _ in range(12):
            event = websocket.receive_json()
            events.append(event)
            if event["type"] == "message_done":
                break

    artifact_event = next(event for event in events if event["type"] == "artifact")
    artifact = artifact_event["data"]["artifact"]
    assert artifact["type"] == "webpage"
    assert artifact["previewUrl"] == f"/preview/{conversation['id']}/index.html"
    assert (work_dir / "index.html").exists()

    response = client.get(artifact["previewUrl"])

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "frame-ancestors 'self'" in response.headers["content-security-policy"]
    assert "AgentHub Mock 页面" in response.text


@pytest.mark.asyncio
async def test_file_watcher_reports_modified_file_with_diff_data():
    work_dir = WORKSPACE_ROOT / f"m4-watcher-{uuid4()}"
    work_dir.mkdir(parents=True)
    target = work_dir / "index.html"
    target.write_text("<h1>Old</h1>\n", encoding="utf-8")
    service = FileWatcherService()

    await service.start_watching("conv-1", str(work_dir))
    target.write_text("<h1>New</h1>\n<p>Added</p>\n", encoding="utf-8")
    changes = await service.get_changes("conv-1")

    assert len(changes) == 1
    change = changes[0]
    assert change["eventType"] == "modified"
    assert change["path"] == "index.html"
    assert change["diffData"]["file"] == "index.html"
    assert change["diffData"]["additions"] == 2
    assert change["diffData"]["deletions"] == 1
    assert "+<p>Added</p>" in change["diffData"]["hunks"][0]["content"]
