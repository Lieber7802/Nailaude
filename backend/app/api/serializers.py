from app.models.agent import Agent, AgentPlatform
from app.models.artifact import Artifact
from app.models.conversation import Conversation
from app.models.message import Message


def serialize_platform(platform: AgentPlatform) -> dict:
    return {
        "id": platform.id,
        "name": platform.name,
        "binaryPath": platform.binary_path,
        "config": platform.config,
        "status": platform.status,
    }


def serialize_agent(agent: Agent) -> dict:
    return {
        "id": agent.id,
        "name": agent.name,
        "avatar": agent.avatar,
        "description": agent.description,
        "capabilities": agent.capabilities,
        "systemInstruction": agent.system_instruction,
        "platformId": agent.platform_id,
        "isBuiltin": agent.is_builtin,
        "createdAt": agent.created_at.isoformat(),
    }


def serialize_conversation(conversation: Conversation, last_message: str | None = None) -> dict:
    data = {
        "id": conversation.id,
        "title": conversation.title,
        "type": conversation.type,
        "workDir": conversation.work_dir,
        "participantIds": conversation.participant_ids,
        "createdBy": conversation.created_by or "local-user",
        "createdAt": conversation.created_at.isoformat(),
        "updatedAt": conversation.updated_at.isoformat(),
    }
    if last_message is not None:
        data["lastMessage"] = last_message
    return data


def serialize_message(
    message: Message,
    artifacts: list[Artifact] | None = None,
    agent_name: str | None = None,
) -> dict:
    data = {
        "id": message.id,
        "conversationId": message.conversation_id,
        "role": message.role,
        "agentId": message.agent_id,
        "content": message.content,
        "contentType": message.content_type,
        "artifacts": [serialize_artifact(artifact) for artifact in artifacts or []],
        "parentMessageId": message.parent_message_id,
        "metadata": message.meta,
        "mentions": [
            {
                "agentId": mention.get("agentId") or mention.get("agent_id"),
                "agentName": mention.get("agentName") or mention.get("agent_name"),
            }
            for mention in message.mentions
        ],
        "createdAt": message.created_at.isoformat(),
    }
    if agent_name:
        data["agentName"] = agent_name
    return data


def serialize_artifact(artifact: Artifact) -> dict:
    return {
        "id": artifact.id,
        "messageId": artifact.message_id,
        "type": artifact.type,
        "title": artifact.title,
        "files": artifact.files,
        "diffData": artifact.diff_data,
        "version": artifact.version,
        "previousVersionId": artifact.previous_version_id,
        "previewUrl": artifact.preview_url or None,
        "createdAt": artifact.created_at.isoformat(),
    }
