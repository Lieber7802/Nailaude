"""
Project State Service - Maintain auto-updated project state document.
"""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.project_state import ProjectState
from app.config import settings
from app.services.collaboration_summarizers import ProjectStateSummarizer
from app.services.git_inspector import GitInspector
from app.services.workspace_scanner import WorkspaceScanner


class ProjectStateService:
    """Maintains a summary of the project state for agent context."""

    def __init__(
        self,
        db: AsyncSession,
        scanner: WorkspaceScanner | None = None,
        git_inspector: GitInspector | None = None,
        summarizer=None,
    ):
        self.db = db
        self.scanner = scanner or WorkspaceScanner()
        self.git_inspector = git_inspector or GitInspector()
        self.summarizer = summarizer or (ProjectStateSummarizer() if settings.DEEPSEEK_API_KEY else None)

    async def get_state(self, conversation_id: str) -> ProjectState | None:
        """Get current project state."""
        return await self.db.scalar(select(ProjectState).where(ProjectState.conversation_id == conversation_id))

    async def refresh(self, conversation: Conversation, task_results: list[dict] | None = None) -> ProjectState:
        """Refresh deterministic facts and optionally summarize incremental changes."""
        scan = self.scanner.scan(conversation.work_dir)
        existing = await self.get_state(conversation.id)
        state = existing or ProjectState(conversation_id=conversation.id)
        recent_changes = self._recent_changes(task_results or [])
        changed = not existing or state.workspace.get("fingerprint") != scan.fingerprint or bool(recent_changes)
        if existing and not changed:
            return existing
        state.workspace = {
            "name": scan.name,
            "workDir": scan.work_dir,
            "scannedAt": datetime.now(timezone.utc).isoformat(),
            "fingerprint": scan.fingerprint,
        }
        state.file_tree = {"totalFiles": scan.total_files, "paths": scan.paths, "truncated": scan.truncated}
        state.git = self.git_inspector.inspect(scan.work_dir)
        state.warnings = scan.warnings
        if recent_changes:
            state.recent_changes = [*(state.recent_changes or []), *recent_changes][-100:]
        if existing and changed:
            state.version += 1
        if changed and self.summarizer:
            try:
                state.progress_summary = await self.summarizer(state, task_results or [])
            except Exception:
                state.progress_summary = state.progress_summary or self._fallback_progress_summary(task_results or [])
        self.db.add(state)
        await self.db.commit()
        await self.db.refresh(state)
        return state

    def _recent_changes(self, task_results: list[dict]) -> list[dict]:
        now = datetime.now(timezone.utc).isoformat()
        changes = []
        for result in task_results:
            audit = result.get("audit") or {}
            for change_type, key in (("created", "filesCreated"), ("modified", "filesModified"), ("deleted", "filesDeleted")):
                for path in audit.get(key) or []:
                    changes.append(
                        {
                            "file": str(path),
                            "changeType": change_type,
                            "summary": f"{change_type} by {result.get('taskId', 'task')}",
                            "source": "agent",
                            "agentId": result.get("agentId"),
                            "taskId": result.get("taskId"),
                            "batchId": result.get("batchId"),
                            "createdAt": now,
                        }
                    )
        return changes

    def _fallback_progress_summary(self, task_results: list[dict]) -> str:
        completed = sum(1 for result in task_results if result.get("status") == "success")
        failed = sum(1 for result in task_results if result.get("status") == "failed")
        changed_files = sorted(
            {
                path
                for result in task_results
                for path in (result.get("filesChanged") or (result.get("audit") or {}).get("filesChanged") or [])
            }
        )
        if completed or failed or changed_files:
            parts = [f"已完成 {completed} 个任务"]
            if failed:
                parts.append(f"{failed} 个任务失败")
            if changed_files:
                parts.append(f"涉及 {len(changed_files)} 个文件变更")
            return "，".join(parts) + "。"
        return "项目状态已更新。"

    async def build_context_summary(self, conversation_id: str) -> str:
        """Build a text summary for agent context injection."""
        state = await self.get_state(conversation_id)
        return state.progress_summary if state else ""


def serialize_project_state(state: ProjectState) -> dict:
    return {
        "conversationId": state.conversation_id,
        "version": state.version,
        "workspace": state.workspace,
        "techStack": state.tech_stack,
        "fileTree": state.file_tree,
        "git": state.git,
        "progressSummary": state.progress_summary,
        "recentChanges": state.recent_changes,
        "warnings": state.warnings,
        "updatedAt": state.updated_at.isoformat(),
    }
