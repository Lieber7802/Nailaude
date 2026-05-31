"""Deterministic Planner result validation."""
from app.schemas.orchestrator import ReadyPlannerResult


class PlanValidationError(ValueError):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


class PlanValidator:
    def validate(self, plan: ReadyPlannerResult, participant_ids: set[str]) -> None:
        errors: list[str] = []
        if len(plan.tasks) > 16:
            errors.append("plan exceeds 16 tasks")
        task_ids = [task.id for task in plan.tasks]
        known = set(task_ids)
        if len(task_ids) != len(known):
            errors.append("task ids must be unique")
        for task in plan.tasks:
            if task.agent_id not in participant_ids:
                errors.append(f"task {task.id} uses non-participant agent {task.agent_id}")
            if task.id in task.depends_on:
                errors.append(f"task {task.id} depends on itself")
            for dependency in task.depends_on:
                if dependency not in known:
                    errors.append(f"task {task.id} depends on unknown task {dependency}")
        if not errors and self._has_cycle(plan):
            errors.append("task graph contains a cycle")
        if errors:
            raise PlanValidationError(errors)

    def _has_cycle(self, plan: ReadyPlannerResult) -> bool:
        graph = {task.id: task.depends_on for task in plan.tasks}
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(task_id: str) -> bool:
            if task_id in visiting:
                return True
            if task_id in visited:
                return False
            visiting.add(task_id)
            if any(visit(dependency) for dependency in graph[task_id]):
                return True
            visiting.remove(task_id)
            visited.add(task_id)
            return False

        return any(visit(task_id) for task_id in graph)
