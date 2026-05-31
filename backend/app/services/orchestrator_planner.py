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
        for attempt in range(2):
            try:
                raw = (await self.client.request_json(build_planner_messages(current_context))).content
                result = self.result_adapter.validate_python(raw)
                if isinstance(result, ReadyPlannerResult):
                    self.validator.validate(result, participant_ids)
                return result
            except (ValidationError, PlanValidationError) as exc:
                if attempt == 1:
                    raise PlannerFailure(f"Planner result invalid after replanning: {exc}") from exc
                current_context["previousValidationErrors"] = (
                    exc.errors if isinstance(exc, PlanValidationError) else [str(exc)]
                )
            except LLMClientError as exc:
                raise PlannerFailure(str(exc)) from exc
        raise PlannerFailure("Planner failed")
