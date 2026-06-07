import { message as antdMessage } from 'antd'
import { lazy, Suspense, useEffect, useMemo, useState } from 'react'
import AddConversationAgentsModal from '../components/chat/AddConversationAgentsModal'
import ChatArea from '../components/chat/ChatArea'
import ConversationList from '../components/chat/ConversationList'
import AgentCreateModal from '../components/chat/AgentCreateModal'
import NewConversationModal from '../components/chat/NewConversationModal'
import Layout from '../components/common/Layout'
import {
  agentApi,
  conversationApi,
  extractMentions,
  formatConversationLastMessage,
  messageApi,
  platformApi,
  type AgentPlatform,
  type CreateAgentInput,
  type CreateConversationInput,
  type Message,
} from '../services/api'
import { useWebSocket } from '../hooks/useWebSocket'
import { useAgentStore } from '../stores/agentStore'
import { useArtifactStore } from '../stores/artifactStore'
import { useConversationStore } from '../stores/conversationStore'
import { useMessageStore } from '../stores/messageStore'
import { useUIStore } from '../stores/uiStore'
import { useOrchestratorStore } from '../stores/orchestratorStore'
import { orchestratorApi } from '../services/orchestratorApi'
import { mergeConversationAgentIds } from '../utils/chatUi'

const EMPTY_MESSAGES: Message[] = []
const PreviewPanel = lazy(() => import('../components/preview/PreviewPanel'))

const Workspace = () => {
  const [createOpen, setCreateOpen] = useState(false)
  const [creating, setCreating] = useState(false)
  const [agentCreateOpen, setAgentCreateOpen] = useState(false)
  const [creatingAgent, setCreatingAgent] = useState(false)
  const [conversationAgentOpen, setConversationAgentOpen] = useState(false)
  const [updatingConversationAgents, setUpdatingConversationAgents] = useState(false)
  const [platforms, setPlatforms] = useState<AgentPlatform[]>([])
  const [loadingPlatforms, setLoadingPlatforms] = useState(false)
  const agents = useAgentStore((state) => state.agents)
  const setAgents = useAgentStore((state) => state.setAgents)
  const addAgent = useAgentStore((state) => state.addAgent)
  const setAgentError = useAgentStore((state) => state.setError)
  const conversations = useConversationStore((state) => state.conversations)
  const activeId = useConversationStore((state) => state.activeId)
  const setConversations = useConversationStore((state) => state.setConversations)
  const addConversation = useConversationStore((state) => state.addConversation)
  const updateConversation = useConversationStore((state) => state.updateConversation)
  const removeConversation = useConversationStore((state) => state.removeConversation)
  const touchConversation = useConversationStore((state) => state.touchConversation)
  const setConversationError = useConversationStore((state) => state.setError)
  const setActive = useConversationStore((state) => state.setActive)
  const messages = useMessageStore((state) =>
    activeId ? state.messagesByConversation[activeId] || EMPTY_MESSAGES : EMPTY_MESSAGES
  )
  const setMessages = useMessageStore((state) => state.setMessages)
  const addMessage = useMessageStore((state) => state.addMessage)
  const setArtifactsFromMessages = useArtifactStore((state) => state.setArtifactsFromMessages)
  const runtime = useUIStore((state) => (activeId ? state.runtimeByConversation[activeId] || null : null))
  const setRuntimeError = useUIStore((state) => state.setRuntimeError)
  const setTeamBoard = useOrchestratorStore((state) => state.setTeamBoard)
  const setProjectState = useOrchestratorStore((state) => state.setProjectState)
  const activeConversation = conversations.find((conversation) => conversation.id === activeId) || null
  const participantAgents = useMemo(
    () => agents.filter((agent) => activeConversation?.participantIds.includes(agent.id)),
    [activeConversation?.participantIds, agents]
  )
  const { send, status } = useWebSocket(activeId)

  useEffect(() => {
    void agentApi
      .list()
      .then(setAgents)
      .catch((error: Error) => {
        setAgentError(error.message)
        void antdMessage.error(error.message)
      })
  }, [setAgentError, setAgents])

  useEffect(() => {
    void conversationApi
      .list(1, 20)
      .then((page) => setConversations(page.items))
      .catch((error: Error) => {
        setConversationError(error.message)
        void antdMessage.error(error.message)
      })
  }, [setConversationError, setConversations])

  useEffect(() => {
    if (!activeId) return
    void messageApi
      .list(activeId)
      .then((page) => {
        setMessages(activeId, page.items)
        setArtifactsFromMessages(page.items)
      })
      .catch((error: Error) => {
        setConversationError(error.message)
        void antdMessage.error(error.message)
      })
  }, [activeId, setArtifactsFromMessages, setConversationError, setMessages])

  useEffect(() => {
    if (!activeId) return
    void Promise.all([orchestratorApi.teamBoard(activeId), orchestratorApi.projectState(activeId)])
      .then(([board, projectState]) => {
        setTeamBoard(activeId, board)
        setProjectState(activeId, projectState)
      })
      .catch(() => undefined)
  }, [activeId, setProjectState, setTeamBoard])

  const handleCreateConversation = async (payload: CreateConversationInput) => {
    setCreating(true)
    try {
      const conversation = await conversationApi.create(payload)
      addConversation(conversation)
      setCreateOpen(false)
      void antdMessage.success('会话已创建')
    } catch (error) {
      const message = error instanceof Error ? error.message : '创建会话失败'
      setConversationError(message)
      void antdMessage.error(message)
    } finally {
      setCreating(false)
    }
  }

  const openAgentCreateModal = () => {
    setAgentCreateOpen(true)
    if (platforms.length > 0 || loadingPlatforms) return
    setLoadingPlatforms(true)
    void platformApi
      .list()
      .then(setPlatforms)
      .catch((error: Error) => {
        setAgentError(error.message)
        void antdMessage.error(error.message)
      })
      .finally(() => setLoadingPlatforms(false))
  }

  const handleAddAgentsToConversation = async (agentIds: string[]) => {
    if (!activeConversation || agentIds.length === 0) return
    setUpdatingConversationAgents(true)
    try {
      const participantIds = mergeConversationAgentIds(activeConversation.participantIds, agentIds)
      const conversation = await conversationApi.update(activeConversation.id, { participantIds })
      updateConversation(conversation)
      setConversationAgentOpen(false)
      void antdMessage.success('智能体已加入当前对话')
    } catch (error) {
      const message = error instanceof Error ? error.message : '添加智能体到对话失败'
      setConversationError(message)
      void antdMessage.error(message)
    } finally {
      setUpdatingConversationAgents(false)
    }
  }

  const handleCreateAgent = async (payload: CreateAgentInput) => {
    setCreatingAgent(true)
    try {
      const agent = await agentApi.create(payload)
      addAgent(agent)
      setAgentCreateOpen(false)
      void antdMessage.success('智能体已添加')
    } catch (error) {
      const message = error instanceof Error ? error.message : '添加智能体失败'
      setAgentError(message)
      void antdMessage.error(message)
    } finally {
      setCreatingAgent(false)
    }
  }

  const handleDeleteConversation = async (id: string) => {
    try {
      await conversationApi.delete(id)
      removeConversation(id)
      void antdMessage.success('会话已删除')
    } catch (error) {
      const message = error instanceof Error ? error.message : '删除会话失败'
      setConversationError(message)
      void antdMessage.error(message)
    }
  }

  const handleSend = (content: string) => {
    if (!activeId) return
    const fallbackAgents = activeConversation?.type === 'single' ? participantAgents : []
    if (activeConversation && participantAgents.length === 0) {
      const message = '当前会话没有参与智能体，无法发送'
      setConversationError(message)
      void antdMessage.warning(message)
      return
    }
    const mentions = extractMentions(content, participantAgents, fallbackAgents)
    const clientMessageId =
      typeof crypto !== 'undefined' && 'randomUUID' in crypto ? crypto.randomUUID() : `client-${Date.now()}`
    const message: Message = {
      id: `local-${Date.now()}`,
      conversationId: activeId,
      role: 'user',
      agentId: null,
      content,
      contentType: 'text',
      artifacts: [],
      parentMessageId: null,
      metadata: { clientMessageId },
      mentions,
      createdAt: new Date().toISOString(),
    }
    const sent = send({
      type: 'send_message',
      data: {
        content,
        mentions,
        parentMessageId: undefined,
        clientMessageId,
      },
    })
    if (!sent) {
      setConversationError('WebSocket 尚未连接，消息未发送')
      void antdMessage.warning('WebSocket 尚未连接')
      return
    }
    setRuntimeError(activeId, null)
    addMessage(message)
    touchConversation(activeId, formatConversationLastMessage('你', content), message.createdAt)
  }

  const handleStop = () => {
    if (!activeId) return
    const sent = send({
      type: 'stop_generation',
      data: { messageId: activeId },
    })
    if (!sent) {
      void antdMessage.warning('WebSocket 尚未连接，无法终止')
      return
    }
    void antdMessage.success('已请求终止当前回复')
  }

  return (
    <>
      <Layout
        left={
          <ConversationList
            activeId={activeId}
            agents={agents}
            conversations={conversations}
            onCreate={() => setCreateOpen(true)}
            onCreateAgent={openAgentCreateModal}
            onDelete={(id) => void handleDeleteConversation(id)}
            onSelect={setActive}
          />
        }
        center={
          <ChatArea
            agents={agents}
            conversation={activeConversation}
            messages={messages}
            runtime={runtime}
            wsStatus={status}
            onAddAgentToConversation={() => setConversationAgentOpen(true)}
            onSend={handleSend}
            onStop={handleStop}
          />
        }
        right={
          <Suspense fallback={<div className="preview-empty">Loading preview...</div>}>
            <PreviewPanel />
          </Suspense>
        }
      />
      <NewConversationModal
        agents={agents}
        creating={creating}
        open={createOpen}
        onCancel={() => setCreateOpen(false)}
        onCreate={handleCreateConversation}
      />
      <AgentCreateModal
        creating={creatingAgent}
        loadingPlatforms={loadingPlatforms}
        open={agentCreateOpen}
        platforms={platforms}
        onCancel={() => setAgentCreateOpen(false)}
        onCreate={handleCreateAgent}
      />
      <AddConversationAgentsModal
        agents={agents}
        open={conversationAgentOpen}
        participantIds={activeConversation?.participantIds || []}
        updating={updatingConversationAgents}
        onAdd={handleAddAgentsToConversation}
        onCancel={() => setConversationAgentOpen(false)}
      />
    </>
  )
}

export default Workspace
