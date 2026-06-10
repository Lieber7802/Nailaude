"""Batch snapshot and read-copy isolation for simple parallel execution."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
import hashlib
from pathlib import Path
import shutil
import tempfile
import uuid

from app.services.workspace_scanner import EXCLUDED_DIRS, WorkspaceScanner
from app.services.workspace_paths import resolve_workspace_path


@dataclass
class BatchSnapshot:
    snapshot_id: str
    source_path: str
    root_path: str
    warnings: list[str] = field(default_factory=list)


@dataclass
class ReadWorkspace:
    snapshot_id: str
    path: str
    batch_id: str = ""
    cancel_event: asyncio.Event | None = None


class WorkspaceSnapshotService:
    def __init__(self, max_file_size: int = 5_000_000, max_total_size: int = 50_000_000):
        self.max_file_size = max_file_size
        self.max_total_size = max_total_size

    def create_batch_snapshot(self, work_dir: str) -> BatchSnapshot:
        root_path = tempfile.mkdtemp(prefix="nailaude-snapshot-")
        source_path = str(Path(root_path, "source"))
        warnings = self._copy_safe(resolve_workspace_path(work_dir), Path(source_path))
        return BatchSnapshot(
            snapshot_id=f"snapshot-{uuid.uuid4()}",
            source_path=source_path,
            root_path=root_path,
            warnings=warnings,
        )

    def create_read_copy(self, snapshot: BatchSnapshot) -> ReadWorkspace:
        target = tempfile.mkdtemp(prefix="read-", dir=snapshot.root_path)
        self._copy_safe(Path(snapshot.source_path), Path(target))
        return ReadWorkspace(snapshot_id=snapshot.snapshot_id, path=target)

    def write_workspace(self, work_dir: str, snapshot: BatchSnapshot) -> ReadWorkspace:
        resolved = resolve_workspace_path(work_dir)
        resolved.mkdir(parents=True, exist_ok=True)
        return ReadWorkspace(snapshot_id=snapshot.snapshot_id, path=str(resolved))

    def capture_workspace_state(self, work_dir: str) -> dict[str, str]:
        """Capture deterministic file hashes for a lightweight task audit."""
        root = resolve_workspace_path(work_dir)
        if not root.exists() or not root.is_dir():
            return {}
        scanner = WorkspaceScanner()
        state: dict[str, str] = {}
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(root)
            if any(part in EXCLUDED_DIRS for part in relative.parts):
                continue
            if not scanner._inside_root(root, path) or scanner._sensitive(path.name):
                continue
            try:
                state[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError:
                continue
        return state

    def diff_workspace_states(self, before: dict[str, str], after: dict[str, str]) -> dict:
        """Return the per-task workspace audit contract."""
        before_paths = set(before)
        after_paths = set(after)
        created = sorted(after_paths - before_paths)
        deleted = sorted(before_paths - after_paths)
        modified = sorted(path for path in before_paths & after_paths if before[path] != after[path])
        changed = sorted({*created, *modified, *deleted})
        return {
            "filesRead": [],
            "filesChanged": changed,
            "filesCreated": created,
            "filesDeleted": deleted,
            "filesModified": modified,
            "diffSummary": ", ".join(changed),
        }

    def cleanup(self, snapshot: BatchSnapshot) -> None:
        shutil.rmtree(snapshot.root_path, ignore_errors=True)

    def _copy_safe(self, source: Path, target: Path) -> list[str]:
        source = source.resolve()
        target.mkdir(parents=True, exist_ok=True)
        scanner = WorkspaceScanner()
        warnings: list[str] = []
        total_size = 0
        for path in sorted(source.rglob("*")):
            relative = path.relative_to(source)
            if any(part in EXCLUDED_DIRS for part in relative.parts):
                continue
            if not scanner._inside_root(source, path) or scanner._sensitive(path.name):
                continue
            destination = target / relative
            if path.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
            elif path.is_file():
                try:
                    size = path.stat().st_size
                except OSError:
                    continue
                if size > self.max_file_size:
                    warnings.append(f"Skipped oversized snapshot file: {relative.as_posix()}")
                    continue
                if total_size + size > self.max_total_size:
                    warnings.append(f"Skipped snapshot file after total-size limit: {relative.as_posix()}")
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, destination)
                total_size += size
        return warnings
