"""
File Watcher Service - Monitor project directories for changes.
"""
from pathlib import Path

from app.services.artifact_service import build_diff_data, infer_language, resolve_work_dir


IGNORED_DIRS = {".git", ".venv", "__pycache__", "node_modules", "dist", "build"}


class FileWatcherService:
    """Watches project directories and generates diff events.

    M4 keeps this dependency-light for tests and demo: callers start a snapshot,
    then poll `get_changes` after an Agent turn. The output shape matches the
    event data needed by ArtifactService and can be backed by watchdog later.
    """

    def __init__(self):
        self._watchers: dict[str, dict] = {}

    async def start_watching(self, conversation_id: str, work_dir: str):
        """Start watching a project directory."""
        root = resolve_work_dir(work_dir)
        root.mkdir(parents=True, exist_ok=True)
        self._watchers[conversation_id] = {"root": root, "snapshot": self._snapshot(root)}

    async def stop_watching(self, conversation_id: str):
        """Stop watching a project directory."""
        self._watchers.pop(conversation_id, None)

    async def get_changes(self, conversation_id: str) -> list:
        """Get pending file changes since last check."""
        watcher = self._watchers.get(conversation_id)
        if watcher is None:
            return []

        root: Path = watcher["root"]
        previous: dict[str, str] = watcher["snapshot"]
        current = self._snapshot(root)
        changes = []

        for path in sorted(current.keys() - previous.keys()):
            content = current[path]
            changes.append(
                {
                    "eventType": "created",
                    "path": path,
                    "files": [{"name": path, "content": content, "language": infer_language(path)}],
                    "oldContent": "",
                    "newContent": content,
                    "diffData": build_diff_data(path, "", content),
                }
            )

        for path in sorted(current.keys() & previous.keys()):
            old_content = previous[path]
            new_content = current[path]
            if old_content == new_content:
                continue
            changes.append(
                {
                    "eventType": "modified",
                    "path": path,
                    "files": [{"name": path, "content": new_content, "language": infer_language(path)}],
                    "oldContent": old_content,
                    "newContent": new_content,
                    "diffData": build_diff_data(path, old_content, new_content),
                }
            )

        for path in sorted(previous.keys() - current.keys()):
            old_content = previous[path]
            changes.append(
                {
                    "eventType": "deleted",
                    "path": path,
                    "files": [],
                    "oldContent": old_content,
                    "newContent": "",
                    "diffData": build_diff_data(path, old_content, ""),
                }
            )

        watcher["snapshot"] = current
        return changes

    def _snapshot(self, root: Path) -> dict[str, str]:
        files: dict[str, str] = {}
        if not root.exists():
            return files

        for path in root.rglob("*"):
            if not path.is_file() or any(part in IGNORED_DIRS for part in path.parts):
                continue
            relative = path.relative_to(root).as_posix()
            try:
                files[relative] = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
        return files
