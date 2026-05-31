import subprocess
import shutil
import uuid

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base
from app.models.conversation import Conversation
from app.services.project_state import ProjectStateService
from app.services.git_inspector import GitInspector
from app.services.workspace_scanner import WorkspaceScanner
from app.schemas.conversation import WORKSPACE_ROOT


@pytest_asyncio.fixture
async def project_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        yield db
    await engine.dispose()


def test_workspace_scanner_filters_sensitive_files_and_truncates(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("print('ok')", encoding="utf-8")
    (tmp_path / ".env").write_text("SECRET=1", encoding="utf-8")
    (tmp_path / ".env.example").write_text("SECRET=", encoding="utf-8")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "ignored.js").write_text("x", encoding="utf-8")

    result = WorkspaceScanner(max_files=2).scan(str(tmp_path))

    assert ".env" not in result.paths
    assert ".env.example" in result.paths
    assert "src/app.py" in result.paths
    assert all("node_modules" not in path for path in result.paths)
    assert result.total_files == 2
    assert result.truncated is False
    assert result.fingerprint


def test_workspace_scanner_marks_truncation(tmp_path):
    for name in ("a.txt", "b.txt", "c.txt"):
        (tmp_path / name).write_text(name, encoding="utf-8")

    result = WorkspaceScanner(max_files=2).scan(str(tmp_path))

    assert len(result.paths) == 2
    assert result.total_files == 3
    assert result.truncated is True


def test_git_inspector_degrades_for_non_git_workspace(tmp_path):
    result = GitInspector().inspect(str(tmp_path))

    assert result["isRepository"] is False
    assert result["dirty"] is False


def test_git_inspector_reads_branch_head_and_dirty_state(tmp_path):
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("hello", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "README.md").write_text("changed", encoding="utf-8")

    result = GitInspector().inspect(str(tmp_path))

    assert result["isRepository"] is True
    assert result["branch"] == "main"
    assert result["headCommit"]
    assert result["dirty"] is True
    assert result["recentCommits"][0]["message"] == "initial"


def test_project_state_api_initializes_workspace_snapshot(client):
    work_dir = WORKSPACE_ROOT / f"pytest-project-state-{uuid.uuid4()}"
    work_dir.mkdir(parents=True)
    (work_dir / "README.md").write_text("hello", encoding="utf-8")
    agents = client.get("/api/v1/agents").json()["data"]
    conversation = client.post(
        "/api/v1/conversations",
        json={"type": "single", "workDir": str(work_dir), "participantIds": [agents[0]["id"]]},
    ).json()["data"]

    response = client.get(f"/api/v1/conversations/{conversation['id']}/project-state")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["conversationId"] == conversation["id"]
    assert "README.md" in payload["fileTree"]["paths"]
    shutil.rmtree(work_dir)


def test_project_state_api_repeated_reads_are_idempotent(client):
    work_dir = WORKSPACE_ROOT / f"pytest-project-state-idempotent-{uuid.uuid4()}"
    work_dir.mkdir(parents=True)
    (work_dir / "README.md").write_text("hello", encoding="utf-8")
    agents = client.get("/api/v1/agents").json()["data"]
    conversation = client.post(
        "/api/v1/conversations",
        json={"type": "single", "workDir": str(work_dir), "participantIds": [agents[0]["id"]]},
    ).json()["data"]

    first = client.get(f"/api/v1/conversations/{conversation['id']}/project-state").json()["data"]
    second = client.get(f"/api/v1/conversations/{conversation['id']}/project-state").json()["data"]

    assert second["version"] == first["version"]
    assert second["updatedAt"] == first["updatedAt"]
    shutil.rmtree(work_dir)


@pytest.mark.asyncio
async def test_project_state_summarizer_updates_summary_and_degrades_to_warning(project_db, tmp_path):
    conversation = Conversation(title="Summary", type="single", work_dir=str(tmp_path))
    project_db.add(conversation)
    await project_db.commit()
    await project_db.refresh(conversation)

    async def summarize(state, task_results):
        return "Implemented the requested workspace changes."

    state = await ProjectStateService(project_db, summarizer=summarize).refresh(conversation, [])
    assert state.progress_summary == "Implemented the requested workspace changes."

    (tmp_path / "README.md").write_text("changed", encoding="utf-8")

    async def fail_summary(state, task_results):
        raise RuntimeError("offline")

    state = await ProjectStateService(project_db, summarizer=fail_summary).refresh(conversation, [])
    assert state.progress_summary == "Implemented the requested workspace changes."
    assert "Project summary unavailable: offline" in state.warnings


@pytest.mark.asyncio
async def test_project_state_refresh_records_task_audit_and_does_not_bump_unchanged_version(project_db, tmp_path):
    conversation = Conversation(title="Audit", type="single", work_dir=str(tmp_path))
    project_db.add(conversation)
    await project_db.commit()
    await project_db.refresh(conversation)
    service = ProjectStateService(project_db, summarizer=None)

    initial = await service.refresh(conversation)
    initial_version = initial.version
    unchanged = await service.refresh(conversation)
    assert unchanged.version == initial_version

    (tmp_path / "README.md").write_text("created", encoding="utf-8")
    changed = await service.refresh(
        conversation,
        [
            {
                "taskId": "task-1",
                "agentId": "agent-1",
                "batchId": "batch-1",
                "audit": {"filesCreated": ["README.md"], "filesModified": [], "filesDeleted": []},
            }
        ],
    )

    assert changed.version == initial_version + 1
    assert changed.recent_changes[-1]["file"] == "README.md"
    assert changed.recent_changes[-1]["changeType"] == "created"
