from dataclasses import dataclass

import pytest

from app.services.orchestrator_planner import OrchestratorPlanner, PlannerFailure


def task(task_id: str, agent_id: str = "agent-1") -> dict:
    return {
        "id": task_id,
        "title": task_id,
        "agentId": agent_id,
        "agentName": "Agent",
        "objective": "Do work",
        "instruction": "Do work",
        "acceptanceCriteria": ["Done"],
        "constraints": [],
        "accessMode": "read",
        "dependsOn": [],
        "priority": 50,
        "riskHints": {},
    }


@dataclass
class FakeResult:
    content: dict


class FakeClient:
    def __init__(self, outputs: list[dict]):
        self.outputs = outputs
        self.calls = 0

    async def request_json(self, messages):
        output = self.outputs[self.calls]
        self.calls += 1
        return FakeResult(output)


class BrokenClient:
    async def request_json(self, messages):
        raise ImportError("Using SOCKS proxy, but the 'socksio' package is not installed")


@pytest.mark.asyncio
async def test_planner_replans_once_after_invalid_plan():
    client = FakeClient(
        [
            {"status": "ready", "tasks": [task("one", "outside")]},
            {"status": "ready", "reasoningSummary": "fixed", "tasks": [task("one")]},
        ]
    )

    result = await OrchestratorPlanner(client).plan({"userRequest": "build"}, participant_ids={"agent-1"})

    assert result.status == "ready"
    assert client.calls == 2


@pytest.mark.asyncio
async def test_planner_replans_when_explicit_mentions_or_requested_stages_are_omitted():
    context = {
        "userRequest": "@代码工匠 @审查大师 @文档专家 先分析需求，再实现可预览页面，然后审查，最后写 README。",
        "mentions": [
            {"agentId": "agent-code", "agentName": "代码工匠"},
            {"agentId": "agent-review", "agentName": "审查大师"},
            {"agentId": "agent-docs", "agentName": "文档专家"},
        ],
        "participants": [
            {"id": "agent-code", "name": "代码工匠", "description": "", "capabilities": ["代码生成"]},
            {"id": "agent-review", "name": "审查大师", "description": "", "capabilities": ["代码审查"]},
            {"id": "agent-docs", "name": "文档专家", "description": "", "capabilities": ["文档"]},
        ],
    }
    client = FakeClient(
        [
            {
                "status": "ready",
                "reasoningSummary": "too small",
                "tasks": [
                    {**task("generic-index", "agent-code"), "title": "Create index.html", "accessMode": "write"},
                    {**task("generic-readme", "agent-docs"), "title": "Create README.md", "accessMode": "write"},
                ],
            },
            {
                "status": "ready",
                "reasoningSummary": "covered",
                "tasks": [
                    {
                        **task("requirements", "agent-docs"),
                        "title": "需求分析",
                        "instruction": "分析课堂签到系统需求并写需求文档。",
                        "accessMode": "write",
                    },
                    {
                        **task("implementation", "agent-code"),
                        "title": "实现可预览页面",
                        "instruction": "根据需求实现 index.html 课堂签到页面。",
                        "accessMode": "write",
                        "dependsOn": ["requirements"],
                    },
                    {
                        **task("review", "agent-review"),
                        "title": "代码审查",
                        "instruction": "审查 index.html 的质量、安全和性能问题。",
                        "accessMode": "read",
                        "dependsOn": ["implementation"],
                    },
                    {
                        **task("readme", "agent-docs"),
                        "title": "README 文档",
                        "instruction": "编写 README.md，说明功能和使用方式。",
                        "accessMode": "write",
                        "dependsOn": ["review"],
                    },
                ],
            },
        ]
    )

    result = await OrchestratorPlanner(client).plan(
        context,
        participant_ids={"agent-code", "agent-review", "agent-docs"},
    )

    assert client.calls == 2
    assert {item.agent_id for item in result.tasks} == {"agent-code", "agent-review", "agent-docs"}
    assert [item.id for item in result.tasks] == ["requirements", "implementation", "review", "readme"]


@pytest.mark.asyncio
async def test_planner_normalizes_model_status_and_access_mode_casing():
    client = FakeClient(
        [
            {
                "status": "Ready",
                "reasoningSummary": "normalized",
                "tasks": [{**task("one"), "accessMode": "Write"}],
            },
        ]
    )

    result = await OrchestratorPlanner(client).plan({"userRequest": "build"}, participant_ids={"agent-1"})

    assert result.status == "ready"
    assert result.tasks[0].access_mode == "write"


@pytest.mark.asyncio
async def test_planner_normalizes_common_loose_task_fields():
    client = FakeClient(
        [
            {
                "status": "Ready",
                "reasoningSummary": "normalized",
                "tasks": [
                    {
                        "id": "one",
                        "agent": "agent-1",
                        "instructions": ["Create output.txt"],
                        "acceptanceCriteria": "output.txt exists",
                        "dependencies": [],
                    }
                ],
            },
        ]
    )

    result = await OrchestratorPlanner(client).plan(
        {"userRequest": "创建 output.txt"}, participant_ids={"agent-1"}
    )

    assert result.status == "ready"
    assert result.tasks[0].agent_id == "agent-1"
    assert result.tasks[0].title == "one"
    assert result.tasks[0].instruction == "Create output.txt"
    assert result.tasks[0].acceptance_criteria == ["output.txt exists"]
    assert result.tasks[0].access_mode == "write"


@pytest.mark.asyncio
async def test_planner_forces_write_access_for_implementation_tasks_even_if_model_says_read():
    client = FakeClient(
        [
            {
                "status": "Ready",
                "reasoningSummary": "normalized",
                "tasks": [
                    {
                        **task("one"),
                        "objective": "根据需求文档实现学生课程签到系统的完整代码。",
                        "instruction": "完成代码实现，生成可运行页面和项目文件。",
                        "accessMode": "read",
                    }
                ],
            },
        ]
    )

    result = await OrchestratorPlanner(client).plan(
        {"userRequest": "@代码工匠 根据刚才产出的需求文档，完成代码实现"},
        participant_ids={"agent-1"},
    )

    assert result.tasks[0].access_mode == "write"


@pytest.mark.asyncio
async def test_planner_forces_write_access_for_document_producing_stages():
    client = FakeClient(
        [
            {
                "status": "ready",
                "tasks": [
                    {
                        **task("requirements"),
                        "title": "Requirements analysis",
                        "objective": "Analyze requirements for the app.",
                        "instruction": "Analyze requirements for the app.",
                        "accessMode": "read",
                    }
                ],
            },
        ]
    )

    result = await OrchestratorPlanner(client).plan(
        {"userRequest": "Create an app"}, participant_ids={"agent-1"}
    )

    assert result.tasks[0].access_mode == "write"


@pytest.mark.asyncio
async def test_planner_treats_task_only_output_as_ready():
    client = FakeClient(
        [
            {
                "tasks": [
                    {
                        "id": "one",
                        "agentId": "agent-1",
                        "instruction": "Create output.txt",
                        "readWriteAccess": "write",
                        "acceptanceCriteria": ["output.txt exists"],
                    }
                ],
            },
        ]
    )

    result = await OrchestratorPlanner(client).plan(
        {"userRequest": "创建 output.txt"}, participant_ids={"agent-1"}
    )

    assert result.status == "ready"
    assert result.tasks[0].access_mode == "write"


@pytest.mark.asyncio
async def test_planner_normalizes_nested_plan_output():
    client = FakeClient(
        [
            {
                "plan": {
                    "tasks": [
                        {
                            "id": "one",
                            "description": "创建 output.txt",
                            "agentId": "agent-1",
                            "writeResources": ["output.txt"],
                            "acceptanceCriteria": "output.txt exists",
                        }
                    ],
                    "dependencies": [],
                },
            },
        ]
    )

    result = await OrchestratorPlanner(client).plan(
        {"userRequest": "创建 output.txt"}, participant_ids={"agent-1"}
    )

    assert result.status == "ready"
    assert result.tasks[0].instruction == "创建 output.txt"
    assert result.tasks[0].access_mode == "write"


@pytest.mark.asyncio
async def test_planner_stops_after_second_invalid_plan():
    client = FakeClient(
        [
            {"status": "ready", "tasks": [task("one", "outside")]},
            {"status": "ready", "tasks": [task("two", "outside")]},
        ]
    )

    with pytest.raises(PlannerFailure, match="invalid after replanning"):
        await OrchestratorPlanner(client).plan({"userRequest": "build"}, participant_ids={"agent-1"})


@pytest.mark.asyncio
async def test_planner_wraps_unexpected_client_errors():
    with pytest.raises(PlannerFailure, match="Using SOCKS proxy"):
        await OrchestratorPlanner(BrokenClient()).plan({"userRequest": "build"}, participant_ids={"agent-1"})


def test_resolve_agent_id_by_name_when_llm_hallucinates_id():
    planner = OrchestratorPlanner.__new__(OrchestratorPlanner)
    context = {
        "participants": [
            {"id": "real-id-1", "name": "代码工匠", "description": "code agent", "capabilities": ["code"]},
            {"id": "real-id-2", "name": "审查大师", "description": "review agent", "capabilities": ["review"]},
        ]
    }
    task_data = task("one", "fake-hallucinated-id")
    task_data["agentName"] = "代码工匠"
    planner._resolve_agent_id(task_data, context)
    assert task_data["agentId"] == "real-id-1"
    assert task_data["agentName"] == "代码工匠"


def test_resolve_agent_id_does_not_override_valid_id():
    planner = OrchestratorPlanner.__new__(OrchestratorPlanner)
    context = {
        "participants": [
            {"id": "real-id-1", "name": "代码工匠", "description": "", "capabilities": []},
        ]
    }
    task_data = task("one", "real-id-1")
    planner._resolve_agent_id(task_data, context)
    assert task_data["agentId"] == "real-id-1"


def test_resolve_agent_id_from_nested_agent_object():
    planner = OrchestratorPlanner.__new__(OrchestratorPlanner)
    context = {
        "participants": [
            {"id": "real-id-2", "name": "审查大师", "description": "", "capabilities": []},
        ]
    }
    task_data = {
        "id": "one",
        "agent": {"name": "审查大师", "id": "fake-id"},
        "title": "Review",
        "objective": "Review code",
        "instruction": "Review code",
        "acceptanceCriteria": ["Done"],
        "accessMode": "read",
        "dependsOn": [],
    }
    planner._resolve_agent_id(task_data, context)
    assert task_data["agentId"] == "real-id-2"


def test_resolve_agent_id_no_match_keeps_original():
    planner = OrchestratorPlanner.__new__(OrchestratorPlanner)
    context = {
        "participants": [
            {"id": "real-id-1", "name": "代码工匠", "description": "", "capabilities": []},
        ]
    }
    task_data = task("one", "completely-unknown")
    task_data["agentName"] = "未知代理"
    planner._resolve_agent_id(task_data, context)
    assert task_data["agentId"] == "completely-unknown"


@pytest.mark.asyncio
async def test_planner_normalizes_deepseek_loose_task_aliases_and_dependency_table():
    client = FakeClient(
        [
            {
                "tasks": [
                    {
                        "taskId": "requirements",
                        "description": "Write requirements for a Pomodoro app.",
                        "assignedAgentId": "agent-docs",
                        "readAccess": [],
                        "writeAccess": ["requirements.md"],
                        "acceptanceCriteria": "requirements.md exists",
                    },
                    {
                        "taskId": "implementation",
                        "description": "Implement the Pomodoro app.",
                        "agentId": "agent-code",
                        "read": ["requirements.md"],
                        "write": ["index.html"],
                        "acceptanceCriteria": "index.html works",
                    },
                    {
                        "taskId": "review",
                        "description": "Review the Pomodoro app code.",
                        "agent": "agent-review",
                        "access": ["read"],
                        "acceptanceCriteria": "review is complete",
                    },
                ],
                "dependencies": [["implementation", "requirements"], ["review", "implementation"]],
            },
        ]
    )
    context = {
        "userRequest": "@Code @Review @Docs create a Pomodoro app",
        "mentions": [
            {"agentId": "agent-code", "agentName": "Code"},
            {"agentId": "agent-review", "agentName": "Review"},
            {"agentId": "agent-docs", "agentName": "Docs"},
        ],
        "participants": [
            {"id": "agent-code", "name": "Code", "description": "frontend", "capabilities": ["code"]},
            {"id": "agent-review", "name": "Review", "description": "review", "capabilities": ["review"]},
            {"id": "agent-docs", "name": "Docs", "description": "docs", "capabilities": ["documentation"]},
        ],
    }

    result = await OrchestratorPlanner(client).plan(
        context,
        participant_ids={"agent-code", "agent-review", "agent-docs"},
    )

    assert [item.id for item in result.tasks] == ["requirements", "implementation", "review"]
    assert [item.agent_id for item in result.tasks] == ["agent-docs", "agent-code", "agent-review"]
    assert [item.access_mode for item in result.tasks] == ["write", "write", "read"]
    assert result.tasks[1].depends_on == ["requirements"]
    assert result.tasks[2].depends_on == ["implementation"]


@pytest.mark.asyncio
async def test_planner_repairs_invalid_agent_id_from_task_stage_when_possible():
    client = FakeClient(
        [
            {
                "status": "ready",
                "tasks": [
                    {
                        "id": "requirements",
                        "type": "requirements_analysis",
                        "description": "Analyze requirements and write a PRD.",
                        "agentId": "agent-docz",
                        "accessMode": "write",
                        "acceptanceCriteria": ["PRD exists"],
                    },
                    {
                        "id": "implementation",
                        "type": "implementation",
                        "description": "Implement the app.",
                        "agentId": "agent-code",
                        "accessMode": "write",
                        "acceptanceCriteria": ["app exists"],
                        "dependencies": ["requirements"],
                    },
                    {
                        "id": "review",
                        "type": "code_review",
                        "description": "Review code quality.",
                        "agentId": "agent-review",
                        "accessMode": "read",
                        "acceptanceCriteria": ["review complete"],
                        "dependencies": ["implementation"],
                    },
                ],
            },
        ]
    )
    context = {
        "userRequest": "@Code @Review @Docs create a Pomodoro app",
        "mentions": [
            {"agentId": "agent-code", "agentName": "Code"},
            {"agentId": "agent-review", "agentName": "Review"},
            {"agentId": "agent-docs", "agentName": "Docs"},
        ],
        "participants": [
            {"id": "agent-code", "name": "Code", "description": "frontend", "capabilities": ["code generation"]},
            {"id": "agent-review", "name": "Review", "description": "quality review", "capabilities": ["code review"]},
            {"id": "agent-docs", "name": "Docs", "description": "technical docs", "capabilities": ["documentation", "requirements analysis"]},
        ],
    }

    result = await OrchestratorPlanner(client).plan(
        context,
        participant_ids={"agent-code", "agent-review", "agent-docs"},
    )

    assert result.tasks[0].agent_id == "agent-docs"


@pytest.mark.asyncio
async def test_planner_enforces_common_app_stage_dependencies():
    client = FakeClient(
        [
            {
                "status": "ready",
                "tasks": [
                    {**task("requirements", "agent-docs"), "title": "Requirements", "accessMode": "write"},
                    {**task("implementation", "agent-code"), "title": "Implementation", "accessMode": "write"},
                    {
                        **task("review", "agent-review"),
                        "title": "Review code",
                        "accessMode": "read",
                        "dependsOn": ["implementation"],
                    },
                    {
                        **task("readme", "agent-docs"),
                        "title": "README documentation",
                        "accessMode": "write",
                        "dependsOn": ["implementation"],
                    },
                ],
            },
        ]
    )
    context = {
        "userRequest": "@Code @Review @Docs create an app, review it, then write README",
        "mentions": [
            {"agentId": "agent-code", "agentName": "Code"},
            {"agentId": "agent-review", "agentName": "Review"},
            {"agentId": "agent-docs", "agentName": "Docs"},
        ],
        "participants": [
            {"id": "agent-code", "name": "Code", "description": "frontend", "capabilities": ["code"]},
            {"id": "agent-review", "name": "Review", "description": "review", "capabilities": ["review"]},
            {"id": "agent-docs", "name": "Docs", "description": "docs", "capabilities": ["documentation"]},
        ],
    }

    result = await OrchestratorPlanner(client).plan(
        context,
        participant_ids={"agent-code", "agent-review", "agent-docs"},
    )

    assert result.tasks[1].depends_on == ["requirements"]
    assert result.tasks[2].depends_on == ["implementation"]
    assert result.tasks[3].depends_on == ["implementation", "review"]
