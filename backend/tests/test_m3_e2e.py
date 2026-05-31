import shutil
import uuid

from app.schemas.conversation import WORKSPACE_ROOT


def test_mock_first_run_refreshes_team_board_and_project_state(client):
    work_dir = WORKSPACE_ROOT / f"pytest-e2e-{uuid.uuid4()}"
    work_dir.mkdir(parents=True)
    (work_dir / "README.md").write_text("demo", encoding="utf-8")
    agents = client.get("/api/v1/agents").json()["data"]
    conversation = client.post(
        "/api/v1/conversations",
        json={"type": "single", "workDir": str(work_dir), "participantIds": [agents[0]["id"]]},
    ).json()["data"]

    with client.websocket_connect(f"/ws/{conversation['id']}") as websocket:
        websocket.send_json({"type": "send_message", "data": {"content": "Build demo", "mentions": []}})
        while True:
            event = websocket.receive_json()
            if event["type"] == "orchestrator_status" and event["data"]["status"] == "completed":
                completed = event["data"]
                break

    board = client.get(f"/api/v1/conversations/{conversation['id']}/team-board").json()["data"]
    state = client.get(f"/api/v1/conversations/{conversation['id']}/project-state").json()["data"]

    assert completed["teamBoardVersion"] >= 1
    assert completed["projectStateVersion"] >= 1
    assert board["recentNotes"][0]["type"] == "decision"
    assert "README.md" in state["fileTree"]["paths"]
    shutil.rmtree(work_dir)
