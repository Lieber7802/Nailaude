from pathlib import Path
from uuid import uuid4

import pytest

from app.schemas.conversation import WORKSPACE_ROOT
from app.services.file_watcher import FileWatcherService
from app.services.preview_service import PreviewService


def test_mock_websocket_generates_webpage_artifact_and_preview_file(client, create_agent):
    agent = create_agent(name="代码工匠 Mock")
    agent_id = agent["id"]
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
                    "mentions": [{"agentId": agent_id, "agentName": agent["name"]}],
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


def test_vite_source_preview_uses_dev_server_proxy(client, monkeypatch, create_agent):
    agent = create_agent(name="Vite Agent")
    work_dir = WORKSPACE_ROOT / f"m5-vite-source-{uuid4()}"
    work_dir.mkdir(parents=True)
    (work_dir / "package.json").write_text(
        '{"scripts":{"dev":"vite"},"dependencies":{"@vitejs/plugin-react":"latest","vite":"latest"}}',
        encoding="utf-8",
    )
    (work_dir / "index.html").write_text(
        '<div id="root"></div><script type="module" src="/src/main.tsx"></script>',
        encoding="utf-8",
    )
    conversation = client.post(
        "/api/v1/conversations",
        json={
            "title": "Vite Preview",
            "type": "single",
            "workDir": str(work_dir),
            "participantIds": [agent["id"]],
        },
    ).json()["data"]
    proxied_urls = []

    async def fake_proxy(self, root, conversation_id, file_path):
        proxied_urls.append((root, conversation_id, file_path))
        return 200, b'<script type="module" src="/src/main.tsx"></script>', "text/html"

    monkeypatch.setattr(PreviewService, "_proxy_vite_dev_server", fake_proxy)

    response = client.get(f"/preview/{conversation['id']}/index.html")

    assert response.status_code == 200
    assert proxied_urls == [(work_dir.resolve(), conversation["id"], "index.html")]
    assert f'/preview/{conversation["id"]}/src/main.tsx' in response.text

    client.get(f"/preview/{conversation['id']}/@vite/client")

    assert proxied_urls[-1] == (work_dir.resolve(), conversation["id"], "@vite/client")


def test_preview_csp_allows_generated_static_pages_with_cdn_runtime(client, create_agent):
    agent = create_agent(name="CDN Preview Agent")
    work_dir = WORKSPACE_ROOT / f"m5-cdn-preview-{uuid4()}"
    work_dir.mkdir(parents=True)
    (work_dir / "index.html").write_text(
        """
        <!doctype html>
        <html>
          <head>
            <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
            <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400&display=swap" rel="stylesheet" />
          </head>
          <body><div id="root"></div><script type="text/babel">React.createElement('div')</script></body>
        </html>
        """,
        encoding="utf-8",
    )
    conversation = client.post(
        "/api/v1/conversations",
        json={
            "title": "CDN Preview",
            "type": "single",
            "workDir": str(work_dir),
            "participantIds": [agent["id"]],
        },
    ).json()["data"]

    response = client.get(f"/preview/{conversation['id']}/index.html")
    csp = response.headers["content-security-policy"]

    assert response.status_code == 200
    assert "script-src 'self' 'unsafe-inline' 'unsafe-eval' https:" in csp
    assert "style-src 'self' 'unsafe-inline' https:" in csp
    assert "font-src 'self' data: https:" in csp
    assert "img-src 'self' data: blob: https:" in csp


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
