import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base
from app.models.conversation import Conversation
from app.models.orchestrator_run import OrchestratorRun
from app.models.project_state import ProjectState
from app.models.task_run import TaskRun
from app.models.team_board import TeamBoard
from app.models.team_note import TeamNote


@pytest.mark.asyncio
async def test_m3_collaboration_models_store_default_snapshots():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        conversation = Conversation(title="M3", type="group", work_dir=".")
        db.add(conversation)
        await db.flush()
        board = TeamBoard(conversation_id=conversation.id)
        state = ProjectState(conversation_id=conversation.id, workspace={"name": "repo"})
        run = OrchestratorRun(conversation_id=conversation.id, user_message_id="message-1")
        db.add_all([board, state, run])
        await db.flush()
        task = TaskRun(run_id=run.id, task_id="task-1", agent_id="agent-1", access_mode="read")
        note = TeamNote(
            conversation_id=conversation.id,
            source_task_id="task-1",
            from_agent_id="agent-1",
            from_agent_name="Builder",
            note_type="heads_up",
            content="Review auth",
            fingerprint="note-1",
        )
        db.add_all([task, note])
        await db.commit()

        assert board.version == 1
        assert board.decisions == []
        assert state.file_tree == {"totalFiles": 0, "paths": [], "truncated": False}
        assert run.status == "queued"
        assert task.status == "pending"
        assert note.status == "active"

    await engine.dispose()


@pytest.mark.asyncio
async def test_team_board_is_unique_per_conversation():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        conversation = Conversation(title="M3", type="group", work_dir=".")
        db.add(conversation)
        await db.flush()
        db.add_all([TeamBoard(conversation_id=conversation.id), TeamBoard(conversation_id=conversation.id)])
        with pytest.raises(IntegrityError):
            await db.commit()

    await engine.dispose()
