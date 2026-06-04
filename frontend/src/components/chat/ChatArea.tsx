import { CheckCircleFilled, EditOutlined, EllipsisOutlined, LoadingOutlined } from '@ant-design/icons'
import { Button } from 'antd'
import { useEffect, useState } from 'react'
import MessageBubble from './MessageBubble'
import MessageInput from './MessageInput'
import type { Agent, Conversation, Message } from '../../services/api'
import type { ConversationRuntimeState } from '../../stores/uiStore'
import { useOrchestratorStore } from '../../stores/orchestratorStore'
import { formatChatTime } from '../../utils/chatUi'
import { visibleCollaborationAgents } from '../../utils/orchestratorUi'
import OrchestratorStatus from '../cards/OrchestratorStatus'
import OrchestratorInputCard from '../cards/OrchestratorInputCard'
import OrchestratorApprovalCard from '../cards/OrchestratorApprovalCard'

interface ChatAreaProps {
  agents: Agent[]
  conversation: Conversation | null
  messages: Message[]
  runtime: ConversationRuntimeState | null
  wsStatus: string
  onCreateAgent: () => void
  onSend: (content: string) => void
  onStop: () => void
}

const ChatArea = ({ agents, conversation, messages, onCreateAgent, onSend, onStop, runtime, wsStatus }: ChatAreaProps) => {
  const participantAgents = agents.filter((agent) => conversation?.participantIds.includes(agent.id))
  const disabled = !conversation || wsStatus !== 'open' || participantAgents.length === 0
  const collaborationLabel = getCollaborationLabel(runtime, wsStatus)
  const currentTime = useMinuteClock()
  const snapshot = useOrchestratorStore((state) => (conversation ? state.snapshots[conversation.id] : undefined))
  const input = useOrchestratorStore((state) => (conversation ? state.inputs[conversation.id] : undefined))
  const approval = useOrchestratorStore((state) => (conversation ? state.approvals[conversation.id] : undefined))
  const canStop = wsStatus === 'open' && hasActiveRun(runtime)

  return (
    <div className="chat-area">
      <header className="chat-area__header">
        <div className="chat-title">
          <div className="chat-title__row">
            <strong>{conversation?.title || '选择或创建会话'}</strong>
            {conversation && (
              <Button aria-label="编辑会话标题" className="icon-button" icon={<EditOutlined />} type="text" />
            )}
          </div>
          <div className="chat-title__chips">
            {participantAgents.map((agent) => (
              <span className="agent-chip" key={agent.id}>
                <span>{agent.avatar}</span>
                {agent.name}
              </span>
            ))}
            {conversation && (
              <button
                className="agent-chip agent-chip--muted agent-chip--button"
                title="添加自定义智能体"
                type="button"
                onClick={onCreateAgent}
              >
                + 添加智能体
              </button>
            )}
          </div>
        </div>
        <div className="chat-actions">
          <span className={`collab-pill collab-pill--${collaborationLabel.tone}`}>
            <CheckCircleFilled />
            {collaborationLabel.text}
          </span>
          <span className="chat-actions__text">{participantAgents.length} 个智能体参与</span>
          <span className="chat-actions__text">更新 {currentTime}</span>
          <Button aria-label="更多操作" className="icon-button" icon={<EllipsisOutlined />} type="text" />
        </div>
      </header>

      <div className="chat-area__body chat-area__body--messages">
        {messages.length === 0 ? (
          <div className="empty-state">发送第一条消息，Mock 智能体会返回流式产物</div>
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
        <RuntimeBanner participantAgents={participantAgents} runtime={runtime} />
        {snapshot && <OrchestratorStatus snapshot={snapshot} />}
        {input && <OrchestratorInputCard runId={input.runId} result={input.result} />}
        {approval && <OrchestratorApprovalCard reason={approval.reason} runId={approval.runId} />}
      </div>

      <MessageInput agents={participantAgents} canStop={canStop} disabled={disabled} onSend={onSend} onStop={onStop} />
    </div>
  )
}

const RuntimeBanner = ({
  participantAgents,
  runtime,
}: {
  participantAgents: Agent[]
  runtime: ConversationRuntimeState | null
}) => {
  if (!runtime) return null
  if (!runtime.error && !runtime.orchestratorStatus && runtime.thinkingAgents.length === 0) return null

  const visibleAgents = visibleCollaborationAgents(participantAgents, runtime.tasks, runtime.thinkingAgents)

  return (
    <article className="collaboration-card">
      <div className="collaboration-card__title">
        <span className="brand-dot">⌂</span>
        <strong>协作状态</strong>
      </div>
      <p>{runtime.error || '所有智能体已同步当前任务状态，您可以查看预览或继续提问。'}</p>
      <div className="collaboration-card__agents">
        {visibleAgents.map((agent) => (
          <span className={agent.status === '思考中' ? 'task-pill task-pill--pending' : 'task-pill'} key={agent.id}>
            {agent.status === '思考中' ? <LoadingOutlined /> : <CheckCircleFilled />}
            {agent.name}
            <strong>{agent.status}</strong>
          </span>
        ))}
      </div>
    </article>
  )
}

const useMinuteClock = () => {
  const [now, setNow] = useState(() => new Date())

  useEffect(() => {
    const timer = window.setInterval(() => setNow(new Date()), 30_000)
    return () => window.clearInterval(timer)
  }, [])

  return formatChatTime(now)
}

const getCollaborationLabel = (runtime: ConversationRuntimeState | null, wsStatus: string) => {
  if (runtime?.error) return { text: '需处理', tone: 'warning' }
  if (runtime?.orchestratorStatus === 'queued') return { text: '排队中', tone: 'active' }
  if (runtime?.orchestratorStatus === 'planning' || runtime?.orchestratorStatus === 'validating') {
    return { text: '分派中', tone: 'active' }
  }
  if (runtime?.orchestratorStatus === 'executing') return { text: '协作中', tone: 'active' }
  if (runtime?.orchestratorStatus === 'summarizing' || runtime?.orchestratorStatus === 'completed') {
    return { text: '已完成', tone: 'done' }
  }
  if (wsStatus === 'open') return { text: '空闲', tone: 'idle' }
  return { text: '连接中', tone: 'idle' }
}

const hasActiveRun = (runtime: ConversationRuntimeState | null) => {
  if (!runtime) return false
  if (runtime.thinkingAgents.length > 0) return true
  if (!runtime.orchestratorStatus) return false
  return !['completed', 'failed', 'cancelled'].includes(runtime.orchestratorStatus)
}

export default ChatArea
