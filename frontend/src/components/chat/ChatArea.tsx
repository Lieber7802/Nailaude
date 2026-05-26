import { Alert, Tag } from 'antd'
import MessageBubble from './MessageBubble'
import MessageInput from './MessageInput'
import type { Agent, Conversation, Message, Task } from '../../services/api'
import type { ConversationRuntimeState } from '../../stores/uiStore'

interface ChatAreaProps {
  agents: Agent[]
  conversation: Conversation | null
  messages: Message[]
  runtime: ConversationRuntimeState | null
  wsStatus: string
  onSend: (content: string) => void
}

const ChatArea = ({ agents, conversation, messages, onSend, runtime, wsStatus }: ChatAreaProps) => {
  const participantAgents = agents.filter((agent) => conversation?.participantIds.includes(agent.id))
  const disabled = !conversation || wsStatus !== 'open' || participantAgents.length === 0

  return (
    <div className="chat-area">
      <header className="chat-area__header">
        <div>
          <strong>{conversation?.title || '选择或创建会话'}</strong>
          <small>{conversation?.workDir || '工作目录未设置'}</small>
        </div>
        <span className={`status-dot status-dot--${wsStatus}`}>{wsStatus}</span>
      </header>
      <RuntimeBanner runtime={runtime} />
      <div className="chat-area__body chat-area__body--messages">
        {messages.length === 0 ? (
          <div className="empty-state">发送第一条消息，Mock Agent 会返回流式产物</div>
        ) : (
          messages.map((message) => (
            <MessageBubble
              agent={agents.find((item) => item.id === message.agentId)}
              isStreaming={Boolean(runtime?.thinkingAgents.includes(message.agentName || ''))}
              key={message.id}
              message={message}
            />
          ))
        )}
      </div>
      <MessageInput agents={participantAgents} disabled={disabled} onSend={onSend} />
    </div>
  )
}

const RuntimeBanner = ({ runtime }: { runtime: ConversationRuntimeState | null }) => {
  if (!runtime) return null
  if (!runtime.error && !runtime.orchestratorStatus && runtime.thinkingAgents.length === 0) return null

  return (
    <>
      {runtime.error && <Alert banner message={runtime.error} type="error" />}
      <div className="runtime-banner">
        {runtime.orchestratorStatus && (
          <Tag color={runtime.orchestratorStatus === 'summarizing' ? 'green' : 'blue'}>
            Orchestrator: {runtime.orchestratorStatus}
          </Tag>
        )}
        {runtime.tasks.map((task) => (
          <TaskTag key={task.id} task={task} />
        ))}
        {runtime.thinkingAgents.map((agentName) => (
          <Tag color="gold" key={agentName}>
            {agentName} 思考中
          </Tag>
        ))}
      </div>
    </>
  )
}

const TaskTag = ({ task }: { task: Task }) => {
  const color = task.status === 'completed' ? 'green' : task.status === 'running' ? 'processing' : 'default'
  return (
    <Tag color={color}>
      {task.agentName}: {task.status}
    </Tag>
  )
}

export default ChatArea
