from app.services.handoff_builder import HandoffBuilder
from app.services.token_estimator import TokenEstimator


def task() -> dict:
    return {
        "id": "task-1",
        "title": "Review auth",
        "agentId": "agent-1",
        "agentName": "Reviewer",
        "objective": "Review authentication changes.",
        "instruction": "Inspect the auth flow.",
        "acceptanceCriteria": ["List concrete issues"],
        "constraints": ["Read only"],
        "accessMode": "read",
        "dependsOn": [],
        "priority": 80,
        "riskHints": {
            "mayDeleteOrRenameFiles": False,
            "mayTouchConfigFiles": False,
            "estimatedFilesTouched": 0,
        },
    }


def test_handoff_builder_keeps_contract_and_compresses_low_priority_notes():
    builder = HandoffBuilder(estimator=TokenEstimator(chars_per_token=1), soft_limit=400, hard_limit=900)
    notes = [{"content": "n" * 300, "type": "heads_up"} for _ in range(10)]

    envelope = builder.build(
        run_id="run-1",
        batch_id="batch-1",
        workspace_path="snapshot",
        snapshot_id="snapshot-1",
        task=task(),
        project_summary="summary",
        team_standards=[],
        relevant_team_notes=notes,
        dependency_results=[],
        navigation_hints={"inspectFirst": ["src/auth.ts"], "changedFiles": [], "diffSummary": ""},
    )

    assert envelope["task"]["id"] == "task-1"
    assert envelope["workspace"]["accessMode"] == "write"
    assert envelope["manifest"]["estimatedTokens"] <= 900
    assert envelope["manifest"]["warnings"]
    assert len(envelope["collaboration"]["relevantTeamNotes"]) < len(notes)
