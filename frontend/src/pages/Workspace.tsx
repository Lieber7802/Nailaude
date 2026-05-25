import { message as antdMessage } from 'antd'
import { useEffect, useMemo, useState } from 'react'
import ChatArea from '../components/chat/ChatArea'
import ConversationList from '../components/chat/ConversationList'
import NewConversationModal from '../components/chat/NewConversationModal'
import Layout from '../components/common/Layout'
import PreviewPanel from '../components/preview/PreviewPanel'
import {
  agentApi,
  conversationApi,
  extractMentions,
  formatConversationLastMessage,
  messageApi,
  type CreateConversationInput,
  type Message,
} from '../services/api'
import { useWebSocket } from '../hooks/useWebSocket'
import { useAgentStore } from '../stores/agentStore'
import { useArtifactStore } from '../stores/artifactStore'
import { useConversationStore } from '../stores/conversationStore'
import { useMessageStore } from '../stores/messageStore'
import { useUIStore } from '../stores/uiStore'

const EMPTY_MESSAGES: Message[] = []

const Workspace = () => {
  const [search, setSearch] = useState('')
  const [createOpen, setCreateOpen] = useState(false)
  const [creating, setCreating] = useState(false)
  const agents = useAgentStore((state) => state.agents)
  const setAgents = useAgentStore((state) => state.setAgents)
  const setAgentError = useAgentStore((state) => state.setError)
  const conversations = useConversationStore((state) => state.conversations)
  const activeId = useConversationStore((state) => state.activeId)
  const setConversations = useConversationStore((state) => state.setConversations)
  const addConversation = useConversationStore((state) => state.addConversation)
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
    const timer = window.setTimeout(() => {
      void conversationApi
        .list(1, 20, search)
        .then((page) => setConversations(page.items))
        .catch((error: Error) => {
          setConversationError(error.message)
          void antdMessage.error(error.message)
        })
    }, 180)
    return () => window.clearTimeout(timer)
  }, [search, setConversationError, setConversations])

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
      const message = '当前会话没有参与 Agent，无法发送'
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

  return (
    <>
      <Layout
        left={
          <ConversationList
            activeId={activeId}
            agents={agents}
            conversations={conversations}
            search={search}
            onCreate={() => setCreateOpen(true)}
            onDelete={(id) => void handleDeleteConversation(id)}
            onSearch={setSearch}
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
            onSend={handleSend}
          />
        }
        right={<PreviewPanel />}
      />
      <NewConversationModal
        agents={agents}
        creating={creating}
        open={createOpen}
        onCancel={() => setCreateOpen(false)}
        onCreate={handleCreateConversation}
      />
    </>
  )
}

export default Workspace
