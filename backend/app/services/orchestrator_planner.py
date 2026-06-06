"""DeepSeek Planner wrapper with one validation-guided replan."""
from copy import deepcopy

from pydantic import TypeAdapter, ValidationError

from app.schemas.orchestrator import PlannerResult, ReadyPlannerResult
from app.services.llm_client import LLMClient, LLMClientError
from app.services.orchestrator_validator import PlanValidationError, PlanValidator
from app.services.planner_prompt import build_planner_messages


class PlannerFailure(RuntimeError):
    pass


STAGE_KEYWORDS = {
    "requirements": {
        "request": ("需求", "requirement", "prd", "spec", "checklist", "分析需求", "需求分析", "验收"),
        "task": ("需求", "requirement", "prd", "spec", "checklist", "需求分析", "验收"),
        "label": "product requirements analysis",
    },
    "implementation": {
        "request": ("实现", "代码", "页面", "预览", "index.html", "html", "implement", "preview"),
        "task": ("实现", "代码", "页面", "预览", "index.html", "html", "implement", "preview"),
        "label": "implementation",
    },
    "review": {
        "request": ("审查", "检查", "audit"),
        "task": ("审查", "检查", "review", "audit"),
        "label": "code review",
    },
    "readme": {
        "request": ("readme", "使用说明", "setup", "usage", "交付文档"),
        "task": ("readme", "使用说明", "setup", "usage", "交付文档"),
        "label": "README documentation",
    },
}


class OrchestratorPlanner:
    def __init__(self, client: LLMClient | None = None, validator: PlanValidator | None = None):
        self.client = client or LLMClient()
        self.validator = validator or PlanValidator()
        self.result_adapter = TypeAdapter(PlannerResult)

    async def plan(self, context: dict, participant_ids: set[str], available_agent_ids: set[str] | None = None):
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
                    self.validator.validate(result, participant_ids, available_agent_ids)
                    self._validate_contextual_coverage(result, current_context)
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
            except Exception as exc:
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
        dependency_map = self._dependency_map(result.get("dependencies"))
        for task in result.get("tasks") or []:
            if not isinstance(task, dict):
                continue
            if "id" not in task:
                task["id"] = task.get("taskId") or task.get("task_id") or task.get("taskID") or task.get("name")
            if "agentId" not in task and "agent_id" not in task:
                agent_id = (
                    task.get("assignedAgentId")
                    or task.get("assigned_agent_id")
                    or task.get("assigneeAgentId")
                    or task.get("assignee_agent_id")
                )
                if agent_id:
                    task["agentId"] = agent_id
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
            if "dependsOn" not in task and "depends_on" not in task and task.get("id") in dependency_map:
                task["dependsOn"] = dependency_map[task["id"]]
            if "riskHints" not in task and "risk_hints" not in task:
                task["riskHints"] = {}
            self._resolve_agent_id(task, context)
            access_mode = (
                task.get("accessMode")
                or task.get("access_mode")
                or task.get("readWriteAccess")
                or self._access_mode_from_aliases(task)
            )
            if isinstance(access_mode, str):
                normalized_access_mode = access_mode.strip().lower()
                task["accessMode"] = normalized_access_mode
                if "access_mode" in task:
                    task["access_mode"] = normalized_access_mode
            elif "accessMode" not in task and "access_mode" not in task:
                task["accessMode"] = (
                    "write"
                    if task.get("writeResources")
                    or task.get("writeAccess")
                    or task.get("write")
                    or self._looks_like_write_task(task, context)
                    or self._stage_implies_write(task)
                    else "read"
                )
        self._enforce_common_stage_dependencies(result.get("tasks") or [])
        return result

    def _dependency_map(self, dependencies: object) -> dict[str, list[str]]:
        mapping: dict[str, list[str]] = {}
        if not isinstance(dependencies, list):
            return mapping
        for item in dependencies:
            task_id = None
            depends_on: object = []
            if isinstance(item, dict):
                task_id = item.get("taskId") or item.get("task_id") or item.get("id") or item.get("task")
                depends_on = item.get("dependsOn") or item.get("depends_on") or item.get("dependencies") or item.get("after") or []
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                task_id = item[0]
                depends_on = item[1:]
            if not task_id:
                continue
            values = depends_on if isinstance(depends_on, list) else [depends_on]
            mapping.setdefault(str(task_id), [])
            for dependency in values:
                if dependency:
                    mapping[str(task_id)].append(str(dependency))
        return mapping

    def _access_mode_from_aliases(self, task: dict) -> str | None:
        for key in ("writeAccess", "write", "writeResources", "write_resources"):
            value = task.get(key)
            if isinstance(value, list) and value:
                return "write"
            if isinstance(value, str) and value.strip():
                return "write"
        access = task.get("access")
        if isinstance(access, str):
            lowered = access.lower()
            if "write" in lowered:
                return "write"
            if "read" in lowered:
                return "read"
        if isinstance(access, list):
            lowered_values = {str(item).strip().lower() for item in access}
            if "write" in lowered_values:
                return "write"
            if "read" in lowered_values:
                return "read"
        for key in ("readAccess", "read", "readResources", "read_resources"):
            value = task.get(key)
            if isinstance(value, list) and value:
                return "read"
            if isinstance(value, str) and value.strip():
                return "read"
        return None

    def _enforce_common_stage_dependencies(self, tasks: list[dict]) -> None:
        by_stage: dict[str, str] = {}
        for task in tasks:
            if not isinstance(task, dict) or not task.get("id"):
                continue
            stage = self._task_stage(task)
            if stage and stage not in by_stage:
                by_stage[stage] = str(task["id"])
        if by_stage.get("requirements") and by_stage.get("implementation"):
            self._add_dependency(tasks, by_stage["implementation"], by_stage["requirements"])
        if by_stage.get("implementation") and by_stage.get("review"):
            self._add_dependency(tasks, by_stage["review"], by_stage["implementation"])
        if by_stage.get("implementation") and by_stage.get("readme"):
            self._add_dependency(tasks, by_stage["readme"], by_stage["implementation"])
        if by_stage.get("review") and by_stage.get("readme"):
            self._add_dependency(tasks, by_stage["readme"], by_stage["review"])

    def _add_dependency(self, tasks: list[dict], task_id: str, dependency_id: str) -> None:
        if task_id == dependency_id:
            return
        task = next((item for item in tasks if isinstance(item, dict) and str(item.get("id")) == task_id), None)
        if task is None:
            return
        depends_on = task.get("dependsOn") or task.get("depends_on") or []
        if not isinstance(depends_on, list):
            depends_on = [depends_on]
        depends_on = [str(item) for item in depends_on if item]
        if dependency_id not in depends_on:
            depends_on.append(dependency_id)
        task["dependsOn"] = depends_on
        if "depends_on" in task:
            task["depends_on"] = depends_on

    def _task_stage(self, task: dict) -> str | None:
        text = " ".join(
            str(value)
            for value in [
                task.get("id"),
                task.get("type"),
                task.get("title"),
                task.get("objective"),
                task.get("instruction"),
                task.get("description"),
            ]
            if value
        ).lower()
        if any(keyword in text for keyword in ("readme", "usage", "setup", "使用说明", "交付文档")):
            return "readme"
        if any(keyword in text for keyword in ("review", "audit", "审查", "评审")):
            return "review"
        if any(keyword in text for keyword in ("implement", "implementation", "实现", "代码", "页面", "预览")):
            return "implementation"
        if any(keyword in text for keyword in ("requirement", "requirements", "prd", "spec", "checklist", "需求", "验收")):
            return "requirements"
        return None

    def _resolve_agent_id(self, task: dict, context: dict) -> None:
        participants = context.get("participants") or []
        participant_ids = {p["id"] for p in participants if isinstance(p, dict) and "id" in p}
        current_id = task.get("agentId") or task.get("agent_id") or ""
        if current_id in participant_ids:
            return
        participant_by_name = {p["name"]: p["id"] for p in participants if isinstance(p, dict) and "name" in p and "id" in p}
        agent_name = task.get("agentName") or ""
        agent_obj = task.get("agent")
        if isinstance(agent_obj, dict):
            agent_name = agent_obj.get("name") or agent_name
        elif isinstance(agent_obj, str):
            agent_name = agent_obj
        if agent_name and agent_name in participant_by_name:
            resolved_id = participant_by_name[agent_name]
            task["agentId"] = resolved_id
            if "agent_id" in task:
                task["agent_id"] = resolved_id
            task["agentName"] = agent_name
            return
        stage = self._task_stage(task)
        preferred = self._preferred_agent_for_stage(stage, participants) if stage else None
        if preferred:
            task["agentId"] = preferred["id"]
            if "agent_id" in task:
                task["agent_id"] = preferred["id"]
            task["agentName"] = preferred["name"]
            return
        inferred_id = self._infer_agent_id_from_task(task, participants)
        if inferred_id:
            task["agentId"] = inferred_id
            if "agent_id" in task:
                task["agent_id"] = inferred_id

    def _preferred_agent_for_stage(self, stage: str | None, participants: list[dict]) -> dict | None:
        if not stage:
            return None
        profiles: list[tuple[dict, str]] = []
        for participant in participants:
            if not isinstance(participant, dict) or not participant.get("id"):
                continue
            profile = " ".join(
                [
                    str(participant.get("name") or ""),
                    str(participant.get("description") or ""),
                    " ".join(str(item) for item in participant.get("capabilities") or []),
                ]
            ).lower()
            profiles.append((participant, profile))

        stage_markers = {
            "requirements": (
                "产品架构",
                "产品",
                "需求分析",
                "prd",
                "spec",
                "checklist",
                "验收",
                "requirements",
            ),
            "implementation": ("代码工匠", "代码生成", "前端", "全栈", "implementation", "code"),
            "review": ("审查大师", "代码审查", "审查", "review", "security", "quality"),
            "readme": ("文档专家", "readme", "使用说明", "交付文档", "technical writing", "技术写作"),
        }.get(stage, ())
        if not stage_markers:
            return None

        best: tuple[int, dict] | None = None
        for participant, profile in profiles:
            score = sum(1 for marker in stage_markers if marker.lower() in profile)
            if score and (best is None or score > best[0]):
                best = (score, participant)
        return best[1] if best else None

    def _infer_agent_id_from_task(self, task: dict, participants: list[dict]) -> str | None:
        stage = " ".join(
            str(value)
            for value in [
                task.get("type"),
                task.get("title"),
                task.get("objective"),
                task.get("instruction"),
                task.get("description"),
            ]
            if value
        ).lower()
        if not stage:
            return None
        stage_keywords = self._stage_keywords(stage)
        if not stage_keywords:
            return None
        best_id = None
        best_score = 0
        for participant in participants:
            if not isinstance(participant, dict) or not participant.get("id"):
                continue
            profile = " ".join(
                [
                    str(participant.get("name") or ""),
                    str(participant.get("description") or ""),
                    " ".join(str(item) for item in participant.get("capabilities") or []),
                ]
            ).lower()
            score = sum(1 for keyword in stage_keywords if keyword in profile)
            if score > best_score:
                best_score = score
                best_id = str(participant["id"])
        return best_id if best_score else None

    def _stage_keywords(self, text: str) -> set[str]:
        if any(keyword in text for keyword in ("requirement", "requirements", "prd", "spec", "checklist", "analysis", "需求")):
            return {"产品架构", "产品", "需求分析", "requirement", "requirements", "prd", "spec", "checklist"}
        if any(keyword in text for keyword in ("implement", "implementation", "code", "frontend", "html", "css", "javascript")):
            return {"code", "frontend", "fullstack", "implementation", "generation"}
        if any(keyword in text for keyword in ("review", "audit", "quality", "security")):
            return {"review", "audit", "quality", "security", "best practice"}
        if any(keyword in text for keyword in ("readme", "documentation", "docs", "document", "使用说明")):
            return {"文档专家", "readme", "documentation", "docs", "technical docs", "writing", "使用说明"}
        return set()

    def _validate_contextual_coverage(self, plan: ReadyPlannerResult, context: dict) -> None:
        errors: list[str] = []
        mentioned_ids = self._mentioned_participant_ids(context)
        if len(mentioned_ids) > 1:
            used_ids = {task.agent_id for task in plan.tasks}
            missing_ids = mentioned_ids - used_ids
            if missing_ids:
                errors.append(
                    "plan must include at least one task for every explicitly mentioned agent; "
                    f"missing agent ids: {', '.join(sorted(missing_ids))}"
                )

        request_text = str(context.get("userRequest") or "").lower()
        plan_text = self._plan_text(plan).lower()
        for stage in STAGE_KEYWORDS.values():
            if any(keyword in request_text for keyword in stage["request"]) and not any(
                keyword in plan_text for keyword in stage["task"]
            ):
                errors.append(f"plan is missing requested {stage['label']} stage")

        if errors:
            raise PlanValidationError(errors)

    def _mentioned_participant_ids(self, context: dict) -> set[str]:
        participants = context.get("participants") or []
        participant_ids = {
            str(agent["id"])
            for agent in participants
            if isinstance(agent, dict) and agent.get("id")
        }
        mentioned_ids = {
            str(mention["agentId"])
            for mention in context.get("mentions") or []
            if isinstance(mention, dict) and mention.get("agentId")
        }
        return mentioned_ids & participant_ids

    def _plan_text(self, plan: ReadyPlannerResult) -> str:
        parts: list[str] = []
        for task in plan.tasks:
            parts.extend(
                [
                    task.id,
                    task.title,
                    task.objective,
                    task.instruction,
                    " ".join(task.acceptance_criteria),
                    task.agent_name,
                ]
            )
        return " ".join(parts)

    def _looks_like_write_task(self, task: dict, context: dict) -> bool:
        text = " ".join(
            str(value)
            for value in [
                task.get("title"),
                task.get("objective"),
                task.get("instruction"),
            ]
            if value
        ).lower()
        return any(
            keyword in text
            for keyword in [
                "build",
                "create",
                "develop",
                "edit",
                "implement",
                "modify",
                "save",
                "write",
                "代码实现",
                "保存",
                "创建",
                "开发",
                "实现",
                "完成代码",
                "撰写",
                "生成",
                "写入",
                "修改",
            ]
        )

    def _stage_implies_write(self, task: dict) -> bool:
        text = " ".join(
            str(value)
            for value in [
                task.get("id"),
                task.get("type"),
                task.get("title"),
                task.get("objective"),
                task.get("instruction"),
                task.get("description"),
            ]
            if value
        ).lower()
        return any(
            keyword in text
            for keyword in (
                "requirement",
                "requirements",
                "prd",
                "implementation",
                "implement",
                "readme",
                "documentation",
            )
        )
