"""Replaceable heuristic token estimator for M3 context budgets."""
import json


class TokenEstimator:
    def __init__(self, chars_per_token: float = 4):
        self.chars_per_token = max(chars_per_token, 0.1)

    def estimate(self, value) -> int:
        text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        return max(1, int(len(text) / self.chars_per_token))
