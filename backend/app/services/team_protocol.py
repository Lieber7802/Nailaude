"""
Team Protocol Service - Team Board and Agent Notes management.
"""
from datetime import datetime, timezone
import hashlib
import json
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team_board import TeamBoard
from app.models.team_note import TeamNote
from app.models.agent import Agent
from app.models.conversation import Conversation
from app.config import settings
from app.services.collaboration_summarizers import TeamBoardSummarizer


class TeamProtocolService:
    """Manages Team Board shared state."""

    def __init__(self, db: AsyncSession, summarizer=None):
        self.db = db
        self.summarizer = summarizer or (TeamBoardSummarizer() if settings.DEEPSEEK_API_KEY else None)
        self.warnings: list[str] = []

    async def get_team_board(self, conversation_id: str) -> TeamBoard:
        """Get the team board for a conversation."""
        board = await self.db.scalar(select(TeamBoard).where(TeamBoard.conversation_id == conversation_id))
        if board is None:
            board = TeamBoard(conversation_id=conversation_id)
            self.db.add(board)
        conversation = await self.db.get(Conversation, conversation_id)
        participant_ids = list(conversation.participant_ids or []) if conversation else []
        agents = await self.db.scalars(select(Agent).where(Agent.id.in_(participant_ids)))
        by_id = {agent.id: agent for agent in agents.all()}
        members = [
            {
                "agentId": agent.id,
                "name": agent.name,
                "role": agent.name,
                "capabilities": list(agent.capabilities or []),
            }
            for agent_id in participant_ids
            if (agent := by_id.get(agent_id))
        ]
        if board.team_members != members:
            board.team_members = members
        await self.db.commit()
        await self.db.refresh(board)
        return board

    async def add_note(self, conversation_id: str, payload: dict) -> TeamNote:
        """Validate, deduplicate, and store one atomic note."""
        note_type = str(payload["type"])
        content = str(payload["content"])[:1000]
        target_type = str(payload.get("toType") or "all")
        target_agent_id = payload.get("toAgentId")
        fingerprint = self._fingerprint(note_type, target_type, target_agent_id, content, payload.get("relatedFiles") or [])
        existing = await self.db.scalar(
            select(TeamNote).where(TeamNote.conversation_id == conversation_id, TeamNote.fingerprint == fingerprint)
        )
        if existing:
            return existing

        note = TeamNote(
            conversation_id=conversation_id,
            source_task_id=str(payload["sourceTaskId"]),
            from_agent_id=str(payload["fromAgentId"]),
            from_agent_name=str(payload["fromAgentName"]),
            to_type=target_type,
            to_agent_id=target_agent_id,
            note_type=note_type,
            content=content,
            related_files=payload.get("relatedFiles") or [],
            related_task_ids=payload.get("relatedTaskIds") or [],
            resolves_note_id=payload.get("resolvesNoteId"),
            fingerprint=fingerprint,
        )
        self.db.add(note)
        if note.note_type == "answer" and note.resolves_note_id:
            question = await self.db.get(TeamNote, note.resolves_note_id)
            if question and question.conversation_id == conversation_id and question.note_type == "question":
                question.status = "resolved"
                question.resolved_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def merge_batch(self, conversation_id: str, task_results: list[dict]) -> TeamBoard:
        """Merge notes only after a batch barrier and refresh deterministic progress."""
        board = await self.get_team_board(conversation_id)
        recent_notes = []
        for result in task_results:
            allowed = {"heads_up", "question"} if result.get("status") == "failed" else {
                "decision", "standard", "heads_up", "question", "answer"
            }
            for raw_note in (result.get("teamNotes") or [])[:10]:
                if raw_note.get("type") not in allowed:
                    continue
                note = await self.add_note(
                    conversation_id,
                    {
                        **raw_note,
                        "sourceTaskId": result["taskId"],
                    },
                )
                serialized = serialize_team_note(note)
                recent_notes.append(serialized)
                if note.note_type == "decision":
                    board.decisions = [
                        *board.decisions,
                        {
                            "id": str(uuid.uuid4()),
                            "content": note.content,
                            "rationale": "",
                            "madeByAgentId": note.from_agent_id,
                            "madeByAgentName": note.from_agent_name,
                            "sourceTaskId": note.source_task_id,
                            "status": self._merged_item_status(result.get("status"), note.content, board.decisions),
                            "createdAt": note.created_at.isoformat(),
                            "updatedAt": note.created_at.isoformat(),
                        },
                    ]
                elif note.note_type == "standard":
                    board.code_standards = [
                        *board.code_standards,
                        {
                            "id": str(uuid.uuid4()),
                            "category": "other",
                            "content": note.content,
                            "sourceTaskId": note.source_task_id,
                            "status": self._merged_item_status(result.get("status"), note.content, board.code_standards),
                            "updatedAt": note.created_at.isoformat(),
                        },
                    ]
        board.recent_notes = recent_notes[-20:]
        board.progress = self._progress(task_results, board.progress)
        if self.summarizer:
            try:
                self._apply_patch(board, await self.summarizer(board, task_results))
            except Exception:
                pass
        board.version += 1
        await self.db.commit()
        await self.db.refresh(board)
        return board

    async def relevant_notes(self, conversation_id: str, agent_id: str, limit: int = 20) -> list[dict]:
        notes = await self.db.scalars(
            select(TeamNote)
            .where(TeamNote.conversation_id == conversation_id, TeamNote.status == "active")
            .order_by(TeamNote.created_at.desc())
        )
        selected = [note for note in notes.all() if note.to_type == "all" or note.to_agent_id == agent_id][:limit]
        now = datetime.now(timezone.utc)
        for note in selected:
            note.injection_count += 1
            note.last_injected_at = now
        await self.db.commit()
        return [serialize_team_note(note) for note in selected]

    def _fingerprint(self, note_type: str, to_type: str, to_agent_id: str | None, content: str, related_files: list) -> str:
        normalized = " ".join(content.lower().split())
        source = json.dumps([note_type, to_type, to_agent_id, normalized, sorted(related_files)], ensure_ascii=False)
        return hashlib.sha256(source.encode("utf-8")).hexdigest()

    def _merged_item_status(self, task_status: str | None, content: str, existing_items: list[dict]) -> str:
        if task_status == "partial":
            return "review_required"
        return "active"

    def _apply_patch(self, board: TeamBoard, patch: dict) -> None:
        if "currentFocus" in patch:
            board.progress = {**board.progress, "currentFocus": str(patch["currentFocus"])[:500]}
        if isinstance(patch.get("openQuestions"), list):
            board.open_questions = list(patch["openQuestions"])[:20]

    def _progress(self, task_results: list[dict], previous: dict) -> dict:
        task_ids = [str(result["taskId"]) for result in task_results]
        completed = list(previous.get("completedTaskIds", []))
        blocked = list(previous.get("blockedTaskIds", []))
        completed.extend(str(result["taskId"]) for result in task_results if result.get("status") == "success")
        blocked.extend(str(result["taskId"]) for result in task_results if result.get("status") == "blocked")
        return {
            "completedTaskIds": list(dict.fromkeys(completed)),
            "activeTaskIds": [],
            "blockedTaskIds": list(dict.fromkeys(blocked)),
            "pendingTaskIds": [item for item in previous.get("pendingTaskIds", []) if item not in task_ids],
            "currentFocus": previous.get("currentFocus", ""),
        }


def serialize_team_note(note: TeamNote) -> dict:
    return {
        "id": note.id,
        "conversationId": note.conversation_id,
        "sourceTaskId": note.source_task_id,
        "fromAgentId": note.from_agent_id,
        "fromAgentName": note.from_agent_name,
        "to": {"type": note.to_type, **({"agentId": note.to_agent_id} if note.to_agent_id else {})},
        "type": note.note_type,
        "content": note.content,
        "relatedFiles": note.related_files,
        "relatedTaskIds": note.related_task_ids,
        "resolvesNoteId": note.resolves_note_id,
        "status": note.status,
        "injectionCount": note.injection_count,
        "lastInjectedAt": note.last_injected_at.isoformat() if note.last_injected_at else None,
        "createdAt": note.created_at.isoformat(),
        "resolvedAt": note.resolved_at.isoformat() if note.resolved_at else None,
    }


def serialize_team_board(board: TeamBoard) -> dict:
    return {
        "conversationId": board.conversation_id,
        "version": board.version,
        "teamMembers": board.team_members,
        "decisions": board.decisions,
        "codeStandards": board.code_standards,
        "openQuestions": board.open_questions,
        "progress": board.progress,
        "recentNotes": board.recent_notes,
        "updatedAt": board.updated_at.isoformat(),
    }
