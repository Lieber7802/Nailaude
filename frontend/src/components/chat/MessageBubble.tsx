import { LoadingOutlined } from '@ant-design/icons'
import CodeCard from '../cards/CodeCard'
import type { Agent, Artifact, Message } from '../../services/api'
import { useArtifactStore } from '../../stores/artifactStore'

interface MessageBubbleProps {
  agent?: Agent
  isStreaming?: boolean
  message: Message
}

const EMPTY_ARTIFACTS: Artifact[] = []

const roleLabel: Record<Message['role'], string> = {
  user: '你',
  agent: 'Agent',
  orchestrator: 'Orchestrator',
  system: 'System',
  team_activity: 'Team',
}

const MessageBubble = ({ agent, isStreaming = false, message }: MessageBubbleProps) => {
  const storedArtifacts = useArtifactStore((state) => state.artifactsByMessage[message.id] || EMPTY_ARTIFACTS)
  const setActiveArtifact = useArtifactStore((state) => state.setActiveArtifact)
  const isUser = message.role === 'user'
  const authorName = isUser ? '你' : message.agentName || agent?.name || roleLabel[message.role]
  const avatar = isUser ? 'U' : agent?.avatar || authorName.slice(0, 1)
  const artifacts = [
    ...message.artifacts,
    ...storedArtifacts.filter((artifact) => !message.artifacts.some((item) => item.id === artifact.id)),
  ]

  return (
    <article className={isUser ? 'message-bubble message-bubble--user' : 'message-bubble'}>
      <div className="message-bubble__meta">
        <span className="message-bubble__author">
          <span className="message-bubble__avatar">{avatar}</span>
          <strong>{authorName}</strong>
          {!isUser && <span className="role-badge">Agent</span>}
          {isStreaming && <LoadingOutlined />}
        </span>
        <span>{formatTime(message.createdAt)}</span>
      </div>
      <div className="message-bubble__content">{message.content || (isStreaming ? '正在生成...' : '')}</div>
      {artifacts.length > 0 && (
        <div className="message-bubble__artifacts">
          {artifacts.map((artifact) => (
            <CodeCard artifact={artifact} key={artifact.id} onOpen={setActiveArtifact} />
          ))}
        </div>
      )}
    </article>
  )
}

const formatTime = (value: string) =>
  new Intl.DateTimeFormat('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(new Date(value))

export default MessageBubble
