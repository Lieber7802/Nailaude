import CodeCard from '../cards/CodeCard'
import type { Artifact, Message } from '../../services/api'
import { useArtifactStore } from '../../stores/artifactStore'

interface MessageBubbleProps {
  message: Message
}

const EMPTY_ARTIFACTS: Artifact[] = []

const MessageBubble = ({ message }: MessageBubbleProps) => {
  const storedArtifacts = useArtifactStore((state) => state.artifactsByMessage[message.id] || EMPTY_ARTIFACTS)
  const setActiveArtifact = useArtifactStore((state) => state.setActiveArtifact)
  const isUser = message.role === 'user'
  const artifacts = [
    ...message.artifacts,
    ...storedArtifacts.filter((artifact) => !message.artifacts.some((item) => item.id === artifact.id)),
  ]

  return (
    <article className={isUser ? 'message-bubble message-bubble--user' : 'message-bubble'}>
      <div className="message-bubble__meta">
        <strong>{isUser ? '你' : message.agentName || 'Agent'}</strong>
        <span>{new Date(message.createdAt).toLocaleTimeString()}</span>
      </div>
      <div className="message-bubble__content">{message.content}</div>
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

export default MessageBubble
