import { LoadingOutlined } from '@ant-design/icons'
import { useState } from 'react'
import CodeCard from '../cards/CodeCard'
import DiffCard from '../cards/DiffCard'
import WebPreviewCard from '../cards/WebPreviewCard'
import type { Agent, Artifact, Message } from '../../services/api'
import { useArtifactStore } from '../../stores/artifactStore'
import { useUIStore } from '../../stores/uiStore'
import { MESSAGE_ARTIFACT_COLLAPSE_LIMIT, getOrderedMessageArtifacts, getVisibleMessageArtifacts } from '../../utils/artifactCard'
import { formatChatTime } from '../../utils/chatUi'
import MessageMarkdown from './MessageMarkdown'

interface MessageBubbleProps {
  agent?: Agent
  isStreaming?: boolean
  message: Message
}

const EMPTY_ARTIFACTS: Artifact[] = []

const roleLabel: Record<Message['role'], string> = {
  user: '你',
  agent: '智能体',
  orchestrator: 'Orchestrator',
  system: 'System',
  team_activity: 'Team',
}

const MessageBubble = ({ agent, isStreaming = false, message }: MessageBubbleProps) => {
  const [artifactsExpanded, setArtifactsExpanded] = useState(false)
  const storedArtifacts = useArtifactStore((state) => state.artifactsByMessage[message.id] || EMPTY_ARTIFACTS)
  const openArtifact = useArtifactStore((state) => state.openArtifact)
  const setPreviewVisible = useUIStore((state) => state.setPreviewVisible)
  const isUser = message.role === 'user'
  const authorName = isUser ? '你' : message.agentName || agent?.name || roleLabel[message.role]
  const avatar = isUser ? 'U' : agent?.avatar || authorName.slice(0, 1)
  const artifacts = getOrderedMessageArtifacts([
    ...message.artifacts,
    ...storedArtifacts.filter((artifact) => !message.artifacts.some((item) => item.id === artifact.id)),
  ])
  const visibleArtifacts = getVisibleMessageArtifacts(artifacts, artifactsExpanded)
  const collapsedHiddenCount = Math.max(0, artifacts.length - MESSAGE_ARTIFACT_COLLAPSE_LIMIT)

  return (
    <article className={isUser ? 'message-bubble message-bubble--user' : 'message-bubble'}>
      <div className="message-bubble__meta">
        <span className="message-bubble__author">
          <span className="message-bubble__avatar">{avatar}</span>
          <strong>{authorName}</strong>
          {!isUser && <span className="role-badge">智能体</span>}
          {isStreaming && <LoadingOutlined />}
        </span>
        <span>{formatChatTime(message.createdAt)}</span>
      </div>
      <div className="message-bubble__content">
        {message.content ? <MessageMarkdown content={message.content} /> : isStreaming ? '正在生成...' : ''}
      </div>
      {artifacts.length > 0 && (
        <div className="message-bubble__artifacts">
          {visibleArtifacts.visibleArtifacts.map((artifact) => (
            <ArtifactCard
              artifact={artifact}
              key={artifact.id}
              onOpen={(item) => {
                setPreviewVisible(true)
                openArtifact(item)
              }}
            />
          ))}
          {visibleArtifacts.canToggle && (
            <button
              className="artifact-list-toggle"
              type="button"
              onClick={() => setArtifactsExpanded((expanded) => !expanded)}
            >
              {artifactsExpanded ? '收起产物列表' : `展开剩余 ${collapsedHiddenCount} 个产物`}
            </button>
          )}
        </div>
      )}
    </article>
  )
}

const ArtifactCard = ({ artifact, onOpen }: { artifact: Artifact; onOpen: (artifact: Artifact) => void }) => {
  const handleOpen = () => onOpen(artifact)
  if (artifact.type === 'diff') return <DiffCard artifact={artifact} onOpen={handleOpen} />
  if (artifact.type === 'webpage') return <WebPreviewCard artifact={artifact} onOpen={handleOpen} />
  return <CodeCard artifact={artifact} onOpen={handleOpen} />
}

export default MessageBubble
