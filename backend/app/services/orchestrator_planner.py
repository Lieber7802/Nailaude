"""DeepSeek Planner wrapper with one validation-guided replan."""
from copy import deepcopy

from pydantic import TypeAdapter, ValidationError

from app.schemas.orchestrator import PlannerResult, ReadyPlannerResult
from app.services.llm_client import LLMClient, LLMClientError
from app.services.orchestrator_validator import PlanValidationError, PlanValidator
from app.services.planner_prompt import build_planner_messages


class PlannerFailure(RuntimeError):
    pass


class OrchestratorPlanner:
    def __init__(self, client: LLMClient | None = None, validator: PlanValidator | None = None):
        self.client = client or LLMClient()
        self.validator = validator or PlanValidator()
        self.result_adapter = TypeAdapter(PlannerResult)

    async def plan(self, context: dict, participant_ids: set[str]):
        current_context = deepcopy(context)
        last_raw: dict | None = None
        for attempt in range(2):
            try:
                raw = self._normalize_raw_result(
                    (await self.client.request_json(build_planner_messages(current_context))).content,
                    current_context,
                )
                last_raw = raw
                result = self.result_adapter.validate_python(raw)
                if isinstance(result, ReadyPlannerResult):
                    self.validator.validate(result, participant_ids)
                return result
            except (ValidationError, PlanValidationError) as exc:
                if attempt == 1:
                    raise PlannerFailure(
                        f"Planner result invalid after replanning: {exc}; normalized_result={last_raw}"
                    ) from exc
                current_context["previousValidationErrors"] = (
                    exc.errors if isinstance(exc, PlanValidationError) else [str(exc)]
                )
            except LLMClientError as exc:
                raise PlannerFailure(str(exc)) from exc
        raise PlannerFailure("Planner failed")

    def _normalize_raw_result(self, raw: dict, context: dict) -> dict:
        if not isinstance(raw, dict):
            return raw
        result = deepcopy(raw)
        if "plan" in result and isinstance(result["plan"], dict):
            result = {**result["plan"], **{key: value for key, value in result.items() if key != "plan"}}
        status = result.get("status")
        if isinstance(status, str):
            result["status"] = status.strip().lower()
        elif result.get("tasks"):
            result["status"] = "ready"
        for task in result.get("tasks") or []:
            if not isinstance(task, dict):
                continue
            agent = task.get("agent")
            if "agentId" not in task and "agent_id" not in task:
                if isinstance(agent, dict):
                    task["agentId"] = agent.get("id") or agent.get("agentId") or agent.get("agent_id")
                    task.setdefault("agentName", agent.get("name") or "")
                elif isinstance(agent, str):
                    task["agentId"] = agent
            if "title" not in task:
                task["title"] = task.get("name") or task.get("description") or task.get("id") or "Task"
            if "objective" not in task:
                task["objective"] = task.get("goal") or task.get("description") or context.get("userRequest") or task["title"]
            if "instruction" not in task:
                instructions = task.get("instructions")
                if isinstance(instructions, list):
                    task["instruction"] = "\n".join(str(item) for item in instructions if str(item).strip())
                elif instructions:
                    task["instruction"] = str(instructions)
                elif task.get("description"):
                    task["instruction"] = str(task["description"])
                else:
                    task["instruction"] = str(task["objective"])
            if "acceptanceCriteria" not in task and "acceptance_criteria" not in task:
                criteria = task.get("acceptance") or task.get("acceptance_criteria") or task.get("criteria")
                task["acceptanceCriteria"] = criteria if isinstance(criteria, list) and criteria else ["Task completed"]
            for criteria_key in ("acceptanceCriteria", "acceptance_criteria"):
                if isinstance(task.get(criteria_key), str):
                    task[criteria_key] = [task[criteria_key]]
            if "dependsOn" not in task and "depends_on" not in task and "dependencies" in task:
                task["dependsOn"] = task.get("dependencies") or []
            if "riskHints" not in task and "risk_hints" not in task:
                task["riskHints"] = {}
            access_mode = task.get("accessMode") or task.get("access_mode") or task.get("readWriteAccess")
            if isinstance(access_mode, str):
                if "accessMode" in task or "readWriteAccess" in task:
                    task["accessMode"] = access_mode.strip().lower()
                if "access_mode" in task:
                    task["access_mode"] = access_mode.strip().lower()
            elif "accessMode" not in task and "access_mode" not in task:
                task["accessMode"] = (
                    "write" if task.get("writeResources") or self._looks_like_write_task(task, context) else "read"
                )
        return result

    def _looks_like_write_task(self, task: dict, context: dict) -> bool:
        text = " ".join(
            str(value)
            for value in [
                task.get("title"),
                task.get("objective"),
                task.get("instruction"),
                context.get("userRequest"),
            ]
            if value
        ).lower()
        return any(keyword in text for keyword in ["create", "write", "modify", "edit", "生成", "创建", "写入", "修改"])
