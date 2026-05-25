from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent, AgentPlatform


BUILTIN_PLATFORMS = [
    {
        "id": "mock",
        "name": "Mock Agent",
        "binary_path": "",
        "config": {},
        "status": "available",
    },
    {
        "id": "llm",
        "name": "LLM Provider",
        "binary_path": "",
        "config": {},
        "status": "unknown",
    },
    {
        "id": "opencode",
        "name": "OpenCode CLI",
        "binary_path": "opencode",
        "config": {},
        "status": "not_installed",
    },
    {
        "id": "codex",
        "name": "Codex CLI",
        "binary_path": "codex",
        "config": {},
        "status": "not_installed",
    },
]


BUILTIN_AGENTS = [
    {
        "name": "代码工匠",
        "avatar": "C",
        "description": "全栈开发专家，擅长生成 React、HTML 和 CSS 代码。",
        "capabilities": ["代码生成", "前端", "全栈"],
        "system_instruction": "你是代码工匠，负责生成清晰、可运行、易维护的代码。",
        "platform_id": "mock",
    },
    {
        "name": "审查大师",
        "avatar": "R",
        "description": "代码审查专家，关注质量、性能和安全。",
        "capabilities": ["代码审查", "最佳实践", "安全"],
        "system_instruction": "你是审查大师，负责指出代码质量、性能和安全问题。",
        "platform_id": "mock",
    },
    {
        "name": "文档专家",
        "avatar": "D",
        "description": "技术文档写手，擅长 PRD、API 文档和 README。",
        "capabilities": ["文档", "需求分析", "技术写作"],
        "system_instruction": "你是文档专家，负责产出结构清晰的技术和产品文档。",
        "platform_id": "mock",
    },
]


async def seed_builtin_data(db: AsyncSession) -> None:
    for platform_data in BUILTIN_PLATFORMS:
        platform = await db.get(AgentPlatform, platform_data["id"])
        if platform is None:
            db.add(AgentPlatform(**platform_data))

    await db.flush()

    for agent_data in BUILTIN_AGENTS:
        existing = await db.scalar(select(Agent).where(Agent.name == agent_data["name"]))
        if existing is None:
            db.add(Agent(**agent_data, is_builtin=True))

    await db.commit()
