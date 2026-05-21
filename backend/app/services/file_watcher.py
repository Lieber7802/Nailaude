"""
File Watcher Service - Monitor project directories for changes.
"""


class FileWatcherService:
    """Watches project directories and generates diff events."""

    def __init__(self):
        self._watchers: dict = {}

    async def start_watching(self, conversation_id: str, work_dir: str):
        """Start watching a project directory."""
        # TODO: implement using watchdog
        pass

    async def stop_watching(self, conversation_id: str):
        """Stop watching a project directory."""
        # TODO: implement
        pass

    async def get_changes(self, conversation_id: str) -> list:
        """Get pending file changes since last check."""
        # TODO: implement
        return []
