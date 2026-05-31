import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base
from app.models.agent import Agent, AgentPlatform
from app.models.conversation import Conversation
from app.services.team_protocol import TeamProtocolService


@pytest_asyncio.fixture
async def team_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        conversation = Conversation(title="Team", type="group", work_dir=".")
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        yield db, conversation
    await engine.dispose()


@pytest.mark.asyncio
async def test_team_protocol_deduplicates_atomic_notes(team_db):
    db, conversation = team_db
    service = TeamProtocolService(db)
    payload = {
        "sourceTaskId": "task-1",
        "fromAgentId": "agent-1",
        "fromAgentName": "Builder",
        "type": "heads_up",
        "content": "Auth flow changed",
        "relatedFiles": ["src/auth.ts"],
    }

    first = await service.add_note(conversation.id, payload)
    second = await service.add_note(conversation.id, payload)

    assert first.id == second.id


@pytest.mark.asyncio
async def test_team_protocol_answer_resolves_question(team_db):
    db, conversation = team_db
    service = TeamProtocolService(db)
    question = await service.add_note(
        conversation.id,
        {
            "sourceTaskId": "task-1",
            "fromAgentId": "agent-1",
            "fromAgentName": "Builder",
            "type": "question",
            "content": "Use JWT?",
        },
    )

    await service.add_note(
        conversation.id,
        {
            "sourceTaskId": "task-2",
            "fromAgentId": "agent-2",
            "fromAgentName": "Reviewer",
            "type": "answer",
            "content": "Use session cookies.",
            "resolvesNoteId": question.id,
        },
    )

    await db.refresh(question)
    assert question.status == "resolved"
    assert question.resolved_at is not None


@pytest.mark.asyncio
async def test_team_protocol_does_not_resolve_question_from_another_conversation(team_db):
    db, conversation = team_db
    other = Conversation(title="Other", type="group", work_dir=".")
    db.add(other)
    await db.commit()
    await db.refresh(other)
    service = TeamProtocolService(db)
    question = await service.add_note(
        conversation.id,
        {
            "sourceTaskId": "task-1",
            "fromAgentId": "agent-1",
            "fromAgentName": "Builder",
            "type": "question",
            "content": "Use JWT?",
        },
    )

    await service.add_note(
        other.id,
        {
            "sourceTaskId": "task-2",
            "fromAgentId": "agent-2",
            "fromAgentName": "Reviewer",
            "type": "answer",
            "content": "Use session cookies.",
            "resolvesNoteId": question.id,
        },
    )

    await db.refresh(question)
    assert question.status == "active"
    assert question.resolved_at is None


@pytest.mark.asyncio
async def test_team_protocol_filters_failed_task_decisions(team_db):
    db, conversation = team_db
    service = TeamProtocolService(db)

    board = await service.merge_batch(
        conversation.id,
        [
            {
                "taskId": "task-1",
                "status": "failed",
                "teamNotes": [
                    {"type": "decision", "content": "Use Redis", "fromAgentId": "agent-1", "fromAgentName": "Builder"},
                    {"type": "heads_up", "content": "Build failed", "fromAgentId": "agent-1", "fromAgentName": "Builder"},
                ],
            }
        ],
    )

    assert board.decisions == []
    assert [note["type"] for note in board.recent_notes] == ["heads_up"]


@pytest.mark.asyncio
async def test_team_protocol_marks_partial_and_ambiguous_decisions_for_review(team_db):
    db, conversation = team_db
    service = TeamProtocolService(db)

    board = await service.merge_batch(
        conversation.id,
        [
            {
                "taskId": "task-1",
                "status": "success",
                "teamNotes": [
                    {"type": "decision", "content": "Use session cookies", "fromAgentId": "agent-1", "fromAgentName": "Builder"},
                ],
            },
            {
                "taskId": "task-2",
                "status": "success",
                "teamNotes": [
                    {"type": "decision", "content": "Use JWT tokens", "fromAgentId": "agent-2", "fromAgentName": "Reviewer"},
                ],
            },
            {
                "taskId": "task-3",
                "status": "partial",
                "teamNotes": [
                    {"type": "standard", "content": "Prefer explicit return types", "fromAgentId": "agent-3", "fromAgentName": "Auditor"},
                ],
            },
        ],
    )

    assert [decision["status"] for decision in board.decisions] == ["active", "active"]
    assert board.code_standards[0]["status"] == "review_required"


@pytest.mark.asyncio
async def test_team_protocol_preserves_completed_progress_across_batches(team_db):
    db, conversation = team_db
    service = TeamProtocolService(db)

    await service.merge_batch(conversation.id, [{"taskId": "task-1", "status": "success", "teamNotes": []}])
    board = await service.merge_batch(conversation.id, [{"taskId": "task-2", "status": "success", "teamNotes": []}])

    assert board.progress["completedTaskIds"] == ["task-1", "task-2"]


@pytest.mark.asyncio
async def test_team_board_populates_members_from_active_conversation(team_db):
    db, conversation = team_db
    db.add(AgentPlatform(id="mock", name="Mock", binary_path="", config={}, status="available"))
    agent = Agent(name="Builder", platform_id="mock", capabilities=["coding"])
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    conversation.participant_ids = [agent.id]
    await db.commit()

    board = await TeamProtocolService(db).get_team_board(conversation.id)

    assert board.team_members == [
        {"agentId": agent.id, "name": "Builder", "role": "Builder", "capabilities": ["coding"]}
    ]


@pytest.mark.asyncio
async def test_team_protocol_applies_summary_patch_and_ignores_summary_failure(team_db):
    db, conversation = team_db

    async def summarize(board, task_results):
        return {"currentFocus": "Review authentication", "openQuestions": [{"id": "q-1", "content": "Use JWT?"}]}

    board = await TeamProtocolService(db, summarizer=summarize).merge_batch(conversation.id, [])
    assert board.progress["currentFocus"] == "Review authentication"
    assert board.open_questions == [{"id": "q-1", "content": "Use JWT?"}]

    async def fail_summary(board, task_results):
        raise RuntimeError("offline")

    service = TeamProtocolService(db, summarizer=fail_summary)
    board = await service.merge_batch(conversation.id, [])
    assert board.progress["currentFocus"] == "Review authentication"
    assert service.warnings == ["Team Board summary unavailable: offline"]


def test_team_board_api_returns_snapshot(client):
    agents = client.get("/api/v1/agents").json()["data"]
    conversation = client.post(
        "/api/v1/conversations",
        json={"type": "single", "workDir": "", "participantIds": [agents[0]["id"]]},
    ).json()["data"]

    response = client.get(f"/api/v1/conversations/{conversation['id']}/team-board")

    assert response.status_code == 200
    assert response.json()["data"]["conversationId"] == conversation["id"]
