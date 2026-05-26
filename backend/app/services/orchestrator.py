"""
Orchestrator Service - rule-based task dispatch for M2 group chats.
"""

from app.models.agent import Agent
from app.models.conversation import Conversation


class OrchestratorService:
    """Builds simple sequential dispatch plans from mentions or participants."""

    async def build_dispatch_plan(
        self,
        conversation: Conversation,
        content: str,
        mentions: list[dict],
        agents: list[Agent],
    ) -> dict:
        selected_agents = self._select_agents(conversation, mentions, agents)
        tasks = []
        previous_task_id: str | None = None

        for index, agent in enumerate(selected_agents, start=1):
            task_id = f"task-{index}"
            tasks.append(
                {
                    "id": task_id,
                    "agentId": agent.id,
                    "agentName": agent.name,
                    "instruction": content,
                    "status": "pending",
                    "dependsOn": previous_task_id,
                }
            )
            previous_task_id = task_id

        return {"tasks": tasks, "executionMode": "sequential"}

    def mark_task(self, plan: dict, task_id: str, status: str, result: str | None = None) -> dict:
        tasks = []
        for task in plan["tasks"]:
            if task["id"] == task_id:
                next_task = {**task, "status": status}
                if result is not None:
                    next_task["result"] = result
                tasks.append(next_task)
            else:
                tasks.append(task)
        return {**plan, "tasks": tasks}

    def _select_agents(self, conversation: Conversation, mentions: list[dict], agents: list[Agent]) -> list[Agent]:
        agents_by_id = {agent.id: agent for agent in agents}
        selected: list[Agent] = []

        for mention in mentions:
            agent_id = mention.get("agentId") or mention.get("agent_id")
            agent = agents_by_id.get(agent_id)
            if agent and agent not in selected:
                selected.append(agent)

        if selected:
            return selected

        for agent_id in conversation.participant_ids or []:
            agent = agents_by_id.get(agent_id)
            if agent and agent not in selected:
                selected.append(agent)

        return selected
