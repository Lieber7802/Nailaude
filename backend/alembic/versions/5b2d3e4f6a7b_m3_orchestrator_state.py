"""m3 orchestrator collaboration state

Revision ID: 5b2d3e4f6a7b
Revises: f3c289e260e9
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "5b2d3e4f6a7b"
down_revision: Union[str, Sequence[str], None] = "f3c289e260e9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "team_boards",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("conversation_id", sa.String(36), sa.ForeignKey("conversations.id"), nullable=False, unique=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("team_members", sa.JSON(), nullable=False),
        sa.Column("decisions", sa.JSON(), nullable=False),
        sa.Column("code_standards", sa.JSON(), nullable=False),
        sa.Column("open_questions", sa.JSON(), nullable=False),
        sa.Column("progress", sa.JSON(), nullable=False),
        sa.Column("recent_notes", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "team_notes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("conversation_id", sa.String(36), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("source_task_id", sa.String(100), nullable=False),
        sa.Column("from_agent_id", sa.String(36), nullable=False),
        sa.Column("from_agent_name", sa.String(100), nullable=False),
        sa.Column("to_type", sa.String(20), nullable=False),
        sa.Column("to_agent_id", sa.String(36)),
        sa.Column("note_type", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("related_files", sa.JSON(), nullable=False),
        sa.Column("related_task_ids", sa.JSON(), nullable=False),
        sa.Column("resolves_note_id", sa.String(36)),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("injection_count", sa.Integer(), nullable=False),
        sa.Column("last_injected_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime()),
        sa.UniqueConstraint("conversation_id", "fingerprint", name="uq_team_notes_conversation_fingerprint"),
    )
    op.create_table(
        "project_states",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("conversation_id", sa.String(36), sa.ForeignKey("conversations.id"), nullable=False, unique=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("workspace", sa.JSON(), nullable=False),
        sa.Column("tech_stack", sa.JSON(), nullable=False),
        sa.Column("file_tree", sa.JSON(), nullable=False),
        sa.Column("git", sa.JSON(), nullable=False),
        sa.Column("progress_summary", sa.Text(), nullable=False),
        sa.Column("recent_changes", sa.JSON(), nullable=False),
        sa.Column("warnings", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "orchestrator_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("conversation_id", sa.String(36), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("user_message_id", sa.String(36), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("reasoning_summary", sa.Text(), nullable=False),
        sa.Column("tasks", sa.JSON(), nullable=False),
        sa.Column("batches", sa.JSON(), nullable=False),
        sa.Column("warnings", sa.JSON(), nullable=False),
        sa.Column("latest_snapshot", sa.JSON(), nullable=False),
        sa.Column("clarification_answers", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "task_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("orchestrator_runs.id"), nullable=False),
        sa.Column("task_id", sa.String(100), nullable=False),
        sa.Column("batch_index", sa.Integer(), nullable=False),
        sa.Column("agent_id", sa.String(36), nullable=False),
        sa.Column("access_mode", sa.String(10), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("result_summary", sa.Text(), nullable=False),
        sa.Column("audit", sa.JSON(), nullable=False),
        sa.Column("error", sa.Text()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("run_id", "task_id", name="uq_task_runs_run_task"),
    )


def downgrade() -> None:
    op.drop_table("task_runs")
    op.drop_table("orchestrator_runs")
    op.drop_table("project_states")
    op.drop_table("team_notes")
    op.drop_table("team_boards")
