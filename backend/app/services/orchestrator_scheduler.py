"""Stable static DAG to batch scheduler."""
from app.schemas.orchestrator import PlannedTask


class SchedulerError(ValueError):
    pass


class OrchestratorScheduler:
    def schedule(self, tasks: list[PlannedTask]) -> list[dict]:
        assigned: set[str] = set()
        batches: list[dict] = []
        indexed = list(enumerate(tasks))
        while len(assigned) < len(tasks):
            ready = [
                (index, task)
                for index, task in indexed
                if task.id not in assigned and all(dependency in assigned for dependency in task.depends_on)
            ]
            ready.sort(key=lambda item: (-item[1].priority, item[0]))
            selected: list[PlannedTask] = []
            has_write = False
            selected_agents: set[str] = set()
            for _, task in ready:
                if len(selected) == 3:
                    break
                if task.agent_id in selected_agents:
                    continue
                if task.access_mode == "write" and has_write:
                    continue
                selected.append(task)
                selected_agents.add(task.agent_id)
                has_write = has_write or task.access_mode == "write"
            if not selected:
                raise SchedulerError("unable to schedule task graph")
            batch_index = len(batches)
            batches.append(
                {"id": f"batch-{batch_index + 1}", "index": batch_index, "status": "pending", "taskIds": [task.id for task in selected]}
            )
            assigned.update(task.id for task in selected)
            if len(batches) > 8:
                raise SchedulerError("plan exceeds 8 batches")
        return batches
