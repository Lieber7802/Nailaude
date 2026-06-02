from pathlib import Path
import shutil
import uuid

from app.schemas.conversation import WORKSPACE_ROOT
from app.services.workspace_snapshot import WorkspaceSnapshotService


def test_read_copies_share_snapshot_id_but_are_isolated(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "app.txt").write_text("original", encoding="utf-8")
    (workspace / ".env").write_text("SECRET=1", encoding="utf-8")
    service = WorkspaceSnapshotService()

    snapshot = service.create_batch_snapshot(str(workspace))
    first = service.create_read_copy(snapshot)
    second = service.create_read_copy(snapshot)
    Path(first.path, "app.txt").write_text("changed", encoding="utf-8")

    assert first.snapshot_id == second.snapshot_id == snapshot.snapshot_id
    assert Path(second.path, "app.txt").read_text(encoding="utf-8") == "original"
    assert (workspace / "app.txt").read_text(encoding="utf-8") == "original"
    assert not Path(first.path, ".env").exists()

    service.cleanup(snapshot)


def test_snapshot_skips_oversized_files_and_reports_warning(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "small.txt").write_text("small", encoding="utf-8")
    (workspace / "large.bin").write_bytes(b"x" * 32)
    service = WorkspaceSnapshotService(max_file_size=16, max_total_size=64)

    snapshot = service.create_batch_snapshot(str(workspace))

    assert Path(snapshot.source_path, "small.txt").exists()
    assert not Path(snapshot.source_path, "large.bin").exists()
    assert snapshot.warnings == ["Skipped oversized snapshot file: large.bin"]
    service.cleanup(snapshot)


def test_snapshot_stops_copying_after_total_size_limit(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "a.txt").write_bytes(b"a" * 8)
    (workspace / "b.txt").write_bytes(b"b" * 8)
    service = WorkspaceSnapshotService(max_file_size=16, max_total_size=8)

    snapshot = service.create_batch_snapshot(str(workspace))

    assert Path(snapshot.source_path, "a.txt").exists()
    assert not Path(snapshot.source_path, "b.txt").exists()
    assert snapshot.warnings == ["Skipped snapshot file after total-size limit: b.txt"]
    service.cleanup(snapshot)


def test_snapshot_and_audit_resolve_relative_workspaces_from_project_root():
    workspace_name = f"pytest-relative-snapshot-{uuid.uuid4()}"
    workspace = WORKSPACE_ROOT / workspace_name
    workspace.mkdir(parents=True)
    try:
        (workspace / "app.txt").write_text("hello", encoding="utf-8")
        service = WorkspaceSnapshotService()

        snapshot = service.create_batch_snapshot(f"workspaces/{workspace_name}")
        state = service.capture_workspace_state(f"workspaces/{workspace_name}")

        assert Path(snapshot.source_path, "app.txt").read_text(encoding="utf-8") == "hello"
        assert "app.txt" in state
        service.cleanup(snapshot)
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_write_workspace_creates_relative_workspace_from_project_root():
    workspace_name = f"pytest-relative-write-{uuid.uuid4()}"
    workspace = WORKSPACE_ROOT / workspace_name
    service = WorkspaceSnapshotService()
    snapshot = service.create_batch_snapshot(f"workspaces/{workspace_name}")
    try:
        write_workspace = service.write_workspace(f"workspaces/{workspace_name}", snapshot)

        assert write_workspace.path == str(workspace)
        assert workspace.is_dir()
    finally:
        service.cleanup(snapshot)
        shutil.rmtree(workspace, ignore_errors=True)
