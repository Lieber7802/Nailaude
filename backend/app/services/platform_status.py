"""Platform status refresh helpers."""
import shutil

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import AgentPlatform
from app.services.agent_manager import AgentManagerService


class PlatformStatusService:
    def __init__(self, manager: AgentManagerService | None = None):
        self.manager = manager or AgentManagerService()

    async def refresh_platforms(self, db: AsyncSession, platforms: list[AgentPlatform]) -> list[AgentPlatform]:
        changed = False
        for platform in platforms:
            next_status = await self.status_for(platform)
            if platform.status != next_status:
                platform.status = next_status
                changed = True
        if changed:
            await db.commit()
            for platform in platforms:
                await db.refresh(platform)
        return platforms

    async def refresh_platform(self, db: AsyncSession, platform: AgentPlatform) -> AgentPlatform:
        next_status = await self.status_for(platform)
        if platform.status != next_status:
            platform.status = next_status
            await db.commit()
            await db.refresh(platform)
        return platform

    async def status_for(self, platform: AgentPlatform) -> str:
        if platform.id == "mock":
            return "available"
        if platform.id in {"codex", "opencode"} and not self._binary_available(platform.binary_path or platform.id):
            return "not_installed"
        healthy = await self.manager.check_health(platform.id)
        return "available" if healthy else "error"

    def _binary_available(self, binary_path: str) -> bool:
        return shutil.which(binary_path) is not None
