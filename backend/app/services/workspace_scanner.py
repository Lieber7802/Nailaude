"""Deterministic, security-aware workspace fact scanner."""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

from app.services.workspace_paths import resolve_workspace_path


EXCLUDED_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", "dist", "build", ".vite", ".next"}
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}


@dataclass
class WorkspaceScan:
    name: str
    work_dir: str
    paths: list[str]
    total_files: int
    truncated: bool
    fingerprint: str
    warnings: list[str]


class WorkspaceScanner:
    def __init__(self, max_files: int = 5000):
        self.max_files = max_files

    def scan(self, work_dir: str) -> WorkspaceScan:
        root = resolve_workspace_path(work_dir)
        paths: list[str] = []
        fingerprint_parts: list[str] = []
        warnings: list[str] = []
        total_files = 0
        if not root.exists() or not root.is_dir():
            return WorkspaceScan(root.name, str(root), [], 0, False, hashlib.sha256(b"").hexdigest(), ["Workspace missing"])

        for current_root, dirs, files in os.walk(root, followlinks=False):
            current = Path(current_root)
            dirs[:] = sorted(
                name for name in dirs if name not in EXCLUDED_DIRS and self._inside_root(root, current / name)
            )
            for name in sorted(files):
                path = current / name
                if self._sensitive(name) or not self._inside_root(root, path):
                    continue
                try:
                    stat = path.stat()
                except OSError:
                    warnings.append(f"Skipped unreadable path: {path.name}")
                    continue
                relative = path.relative_to(root).as_posix()
                total_files += 1
                fingerprint_parts.append(f"{relative}:{stat.st_size}:{stat.st_mtime_ns}")
                if len(paths) < self.max_files:
                    paths.append(relative)

        digest = hashlib.sha256("\n".join(fingerprint_parts).encode("utf-8")).hexdigest()
        return WorkspaceScan(root.name, str(root), paths, total_files, total_files > self.max_files, digest, warnings)

    def _inside_root(self, root: Path, path: Path) -> bool:
        try:
            path.resolve().relative_to(root)
        except (OSError, ValueError):
            return False
        return True

    def _sensitive(self, name: str) -> bool:
        lowered = name.lower()
        if lowered == ".env.example":
            return False
        return (
            lowered == ".env"
            or lowered.startswith(".env.")
            or Path(lowered).suffix in SENSITIVE_SUFFIXES
            or lowered.startswith("id_rsa")
            or lowered.startswith("credentials")
            or lowered.startswith("secrets")
        )
