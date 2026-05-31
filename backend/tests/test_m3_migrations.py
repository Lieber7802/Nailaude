import os
from pathlib import Path
import sqlite3
import subprocess
import sys


def run_alembic(database_path: Path, revision: str) -> None:
    env = {**os.environ, "ALEMBIC_DATABASE_URL": f"sqlite:///{database_path.as_posix()}"}
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", revision],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )


def table_names(database_path: Path) -> set[str]:
    with sqlite3.connect(database_path) as connection:
        return {row[0] for row in connection.execute("select name from sqlite_master where type = 'table'")}


def test_alembic_upgrade_head_uses_explicit_database_override(tmp_path):
    database_path = tmp_path / "fresh.db"

    run_alembic(database_path, "head")

    assert {"conversations", "orchestrator_runs", "task_runs", "team_boards", "project_states"} <= table_names(database_path)


def test_alembic_upgrades_previous_schema_to_m3(tmp_path):
    database_path = tmp_path / "upgrade.db"

    run_alembic(database_path, "f3c289e260e9")
    assert "orchestrator_runs" not in table_names(database_path)
    run_alembic(database_path, "head")

    assert {"orchestrator_runs", "task_runs", "team_boards", "project_states"} <= table_names(database_path)
