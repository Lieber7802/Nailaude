import {
  CheckCircleFilled,
  CloseCircleFilled,
  EditOutlined,
  EllipsisOutlined,
  ExclamationCircleFilled,
  LoadingOutlined,
  PauseCircleFilled,
} from '@ant-design/icons'
import { Button } from 'antd'
import { useEffect, useState } from 'react'
import MessageBubble from './MessageBubble'
import MessageInput from './MessageInput'
import type { Agent, Conversation, Message } from '../../services/api'
import type { ConversationRuntimeState } from '../../stores/uiStore'
import { useOrchestratorStore } from '../../stores/orchestratorStore'
import { formatChatTime } from '../../utils/chatUi'
import { formatTaskDuration, visibleCollaborationAgents, type VisibleCollaborationAgent } from '../../utils/orchestratorUi'
import OrchestratorStatus from '../cards/OrchestratorStatus'
import OrchestratorInputCard from '../cards/OrchestratorInputCard'
import OrchestratorApprovalCard from '../cards/OrchestratorApprovalCard'

interface ChatAreaProps {
  agents: Agent[]
  conversation: Conversation | null
  messages: Message[]
  runtime: ConversationRuntimeState | null
  wsStatus: string
  onAddAgentToConversation: () => void
  onSend: (content: string) => void
  onStop: () => void
}

const ChatArea = ({
  agents,
  conversation,
  messages,
  onAddAgentToConversation,
  onSend,
  onStop,
  runtime,
  wsStatus,
}: ChatAreaProps) => {
  const participantAgents = agents.filter((agent) => conversation?.participantIds.includes(agent.id))
  const disabled = !conversation || wsStatus !== 'open' || participantAgents.length === 0
  const collaborationLabel = getCollaborationLabel(runtime, wsStatus)
  const currentTime = useClock()
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
                title="从已有智能体中添加到当前对话"
                type="button"
                onClick={onAddAgentToConversation}
              >
                + 添加智能体
              </button>
            )}
          </div>
        </div>
        <div className="chat-actions">
          <span className={`collab-pill collab-pill--${collaborationLabel.tone}`}>
            {collaborationLabelIcon(collaborationLabel.tone)}
            {collaborationLabel.text}
          </span>
          <span className="chat-actions__text">{participantAgents.length} 个智能体参与</span>
          <span className="chat-actions__text">更新 {formatChatTime(currentTime)}</span>
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
        <RuntimeBanner now={currentTime.getTime()} participantAgents={participantAgents} runtime={runtime} />
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
  now,
  runtime,
}: {
  now: number
  participantAgents: Agent[]
  runtime: ConversationRuntimeState | null
}) => {
  if (!runtime) return null
  if (!runtime.error && !runtime.orchestratorStatus && runtime.thinkingAgents.length === 0) return null

  const visibleAgents = visibleCollaborationAgents(
    participantAgents,
    runtime.tasks,
    runtime.thinkingAgents,
    runtime.taskTimings,
    now
  )

  return (
    <article className="collaboration-card">
      <div className="collaboration-card__title">
        <span className="brand-dot">⌂</span>
        <strong>协作状态</strong>
      </div>
      <p>{runtime.error || '所有智能体已同步当前任务状态，您可以查看预览或继续提问。'}</p>
      <div className="collaboration-card__agents">
        {visibleAgents.map((agent) => (
          <span className={`task-pill task-pill--${agent.tone}`} key={agent.id}>
            {collaborationStatusIcon(agent)}
            {agent.name}
            <strong>{agent.status}</strong>
            {agent.durationMs !== undefined && (
              <span className="task-pill__duration">耗时 {formatTaskDuration(agent.durationMs)}</span>
            )}
          </span>
        ))}
      </div>
    </article>
  )
}

const useClock = () => {
  const [now, setNow] = useState(() => new Date())

  useEffect(() => {
    const timer = window.setInterval(() => setNow(new Date()), 1_000)
    return () => window.clearInterval(timer)
  }, [])

  return now
}

const getCollaborationLabel = (runtime: ConversationRuntimeState | null, wsStatus: string) => {
  if (runtime?.error) return { text: '需处理', tone: 'warning' }
  if (runtime?.tasks.some((task) => task.status === 'failed' || task.status === 'blocked')) {
    return { text: '需处理', tone: 'warning' }
  }
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

const collaborationStatusIcon = (agent: VisibleCollaborationAgent) => {
  if (agent.tone === 'pending') return <LoadingOutlined />
  if (agent.tone === 'danger') return <CloseCircleFilled />
  if (agent.tone === 'warning') return <ExclamationCircleFilled />
  if (agent.tone === 'idle') return <PauseCircleFilled />
  return <CheckCircleFilled />
}

const collaborationLabelIcon = (tone: string) => {
  if (tone === 'active') return <LoadingOutlined />
  if (tone === 'warning') return <ExclamationCircleFilled />
  if (tone === 'idle') return <PauseCircleFilled />
  return <CheckCircleFilled />
}

const hasActiveRun = (runtime: ConversationRuntimeState | null) => {
  if (!runtime) return false
  if (runtime.thinkingAgents.length > 0) return true
  if (!runtime.orchestratorStatus) return false
  return !['completed', 'failed', 'cancelled'].includes(runtime.orchestratorStatus)
}

export default ChatArea
