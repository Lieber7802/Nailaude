"""Per-conversation FIFO run queue."""
from collections import defaultdict, deque


class QueueFullError(RuntimeError):
    pass


class OrchestratorQueue:
    def __init__(self, max_queued: int = 10):
        self.max_queued = max_queued
        self._queued: dict[str, deque[str]] = defaultdict(deque)
        self._active: dict[str, str] = {}

    def enqueue(self, conversation_id: str, run_id: str) -> int:
        queue = self._queued[conversation_id]
        if len(queue) >= self.max_queued:
            raise QueueFullError("conversation run queue is full")
        queue.append(run_id)
        return len(queue)

    def activate_next(self, conversation_id: str) -> str | None:
        if conversation_id in self._active:
            return None
        queue = self._queued[conversation_id]
        if not queue:
            return None
        self._active[conversation_id] = queue.popleft()
        return self._active[conversation_id]

    def complete_current(self, conversation_id: str) -> str | None:
        return self._active.pop(conversation_id, None)

    def active(self, conversation_id: str) -> str | None:
        return self._active.get(conversation_id)

    def queued_count(self, conversation_id: str) -> int:
        return len(self._queued[conversation_id])
