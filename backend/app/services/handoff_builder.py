"""Compact Agent handoff envelope builder."""
from __future__ import annotations

from copy import deepcopy

from app.services.token_estimator import TokenEstimator


class HandoffBuilder:
    def __init__(self, estimator: TokenEstimator | None = None, soft_limit: int = 16_000, hard_limit: int = 32_000):
        self.estimator = estimator or TokenEstimator()
        self.soft_limit = soft_limit
        self.hard_limit = hard_limit

    def build(
        self,
        *,
        run_id: str,
        batch_id: str,
        workspace_path: str,
        snapshot_id: str,
        task: dict,
        project_summary: str,
        team_standards: list,
        relevant_team_notes: list,
        dependency_results: list,
        navigation_hints: dict,
    ) -> dict:
        envelope = {
            "runId": run_id,
            "taskId": task["id"],
            "batchId": batch_id,
            "workspace": {"path": workspace_path, "accessMode": "write", "snapshotId": snapshot_id},
            "task": deepcopy(task),
            "collaboration": {
                "projectSummary": project_summary,
                "teamStandards": deepcopy(team_standards),
                "relevantTeamNotes": deepcopy(relevant_team_notes[:20]),
                "dependencyResults": deepcopy(dependency_results[:16]),
            },
            "navigationHints": deepcopy(navigation_hints),
            "manifest": {"estimatedTokens": 0, "warnings": [], "omittedItems": []},
        }
        self._compress(envelope)
        return envelope

    def _compress(self, envelope: dict) -> None:
        while self._estimate_payload(envelope) > self.soft_limit:
            collaboration = envelope["collaboration"]
            if collaboration["relevantTeamNotes"]:
                collaboration["relevantTeamNotes"].pop()
                envelope["manifest"]["omittedItems"].append("teamNote")
            elif collaboration["dependencyResults"]:
                collaboration["dependencyResults"].pop()
                envelope["manifest"]["omittedItems"].append("dependencyResult")
            elif envelope["navigationHints"].get("inspectFirst"):
                envelope["navigationHints"]["inspectFirst"].pop()
                envelope["manifest"]["omittedItems"].append("navigationHint")
            else:
                break
        estimated = self._estimate_payload(envelope)
        envelope["manifest"]["estimatedTokens"] = estimated
        if envelope["manifest"]["omittedItems"]:
            envelope["manifest"]["warnings"].append("Handoff compressed to fit context budget")
        if estimated > self.hard_limit:
            envelope["manifest"]["warnings"].append("Handoff exceeds hard context limit")

    def _estimate_payload(self, envelope: dict) -> int:
        payload = {key: value for key, value in envelope.items() if key != "manifest"}
        return self.estimator.estimate(payload)
