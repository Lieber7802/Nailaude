"""Shared workspace path resolution helpers."""
from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def resolve_workspace_path(work_dir: str | Path) -> Path:
    """Resolve Nailaude workspace paths consistently across backend services."""
    path = Path(work_dir).expanduser()
    if path.is_absolute():
        return path.resolve(strict=False)
    if path.parts and path.parts[0] == "workspaces":
        return (PROJECT_ROOT / path).resolve(strict=False)
    return path.resolve(strict=False)
