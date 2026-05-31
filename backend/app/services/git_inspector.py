"""Short-timeout Git metadata inspection with graceful fallback."""
from __future__ import annotations

import subprocess


class GitInspector:
    def __init__(self, timeout: float = 3):
        self.timeout = timeout

    def inspect(self, work_dir: str) -> dict:
        if self._run(work_dir, ["rev-parse", "--is-inside-work-tree"]) != "true":
            return {"isRepository": False, "dirty": False, "recentCommits": []}
        branch = self._run(work_dir, ["branch", "--show-current"])
        head = self._run(work_dir, ["rev-parse", "HEAD"])
        status = self._run(work_dir, ["status", "--short"])
        commits = self._run(work_dir, ["log", "-5", "--pretty=format:%h%x09%s"])
        diff_stat = self._run(work_dir, ["diff", "--stat"])
        return {
            "isRepository": True,
            "branch": branch or None,
            "headCommit": head or None,
            "dirty": bool(status),
            "recentCommits": [
                {"sha": line.split("\t", 1)[0], "message": line.split("\t", 1)[1] if "\t" in line else ""}
                for line in commits.splitlines()
                if line
            ],
            "status": status.splitlines(),
            "diffStat": diff_stat,
        }

    def _run(self, cwd: str, args: list[str]) -> str:
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            return ""
        return result.stdout.strip() if result.returncode == 0 else ""
