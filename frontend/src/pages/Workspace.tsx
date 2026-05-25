import { useEffect } from 'react'
import ChatArea from '../components/chat/ChatArea'
import ConversationList from '../components/chat/ConversationList'
import Layout from '../components/common/Layout'
import PreviewPanel from '../components/preview/PreviewPanel'
import { agentApi, conversationApi, messageApi, type Message } from '../services/api'
import { useWebSocket } from '../hooks/useWebSocket'
import { useAgentStore } from '../stores/agentStore'
import { useArtifactStore } from '../stores/artifactStore'
import { useConversationStore } from '../stores/conversationStore'
import { useMessageStore } from '../stores/messageStore'

const EMPTY_MESSAGES: Message[] = []

const Workspace = () => {
  const agents = useAgentStore((state) => state.agents)
  const setAgents = useAgentStore((state) => state.setAgents)
  const setAgentError = useAgentStore((state) => state.setError)
  const conversations = useConversationStore((state) => state.conversations)
  const activeId = useConversationStore((state) => state.activeId)
  const setConversations = useConversationStore((state) => state.setConversations)
  const addConversation = useConversationStore((state) => state.addConversation)
  const setConversationError = useConversationStore((state) => state.setError)
  const setActive = useConversationStore((state) => state.setActive)
  const messages = useMessageStore((state) => (activeId ? state.messagesByConversation[activeId] || EMPTY_MESSAGES : EMPTY_MESSAGES))
  const setMessages = useMessageStore((state) => state.setMessages)
  const addMessage = useMessageStore((state) => state.addMessage)
  const setArtifactsFromMessages = useArtifactStore((state) => state.setArtifactsFromMessages)
  const activeConversation = conversations.find((conversation) => conversation.id === activeId) || null
  const { send, status } = useWebSocket(activeId)

  useEffect(() => {
    void agentApi
      .list()
      .then(setAgents)
      .catch((error: Error) => setAgentError(error.message))
  }, [setAgentError, setAgents])

  useEffect(() => {
    void conversationApi
      .list()
      .then((page) => setConversations(page.items))
      .catch((error: Error) => setConversationError(error.message))
  }, [setConversationError, setConversations])

  useEffect(() => {
    if (!activeId) return
    void messageApi
      .list(activeId)
      .then((page) => {
        setMessages(activeId, page.items)
        setArtifactsFromMessages(page.items)
      })
      .catch((error: Error) => setConversationError(error.message))
  }, [activeId, setArtifactsFromMessages, setConversationError, setMessages])

  const handleCreateConversation = async () => {
    const firstAgent = agents[0]
    if (!firstAgent) {
      setConversationError('Agent 列表尚未加载完成')
      return
    }

    const conversation = await conversationApi.create({
      title: 'Mock 协作会话',
      type: 'single',
      workDir: 'workspaces/mock-demo',
      participantIds: [firstAgent.id],
    })
    addConversation(conversation)
  }

  const handleSend = (content: string) => {
    if (!activeId) return
    const participantId = activeConversation?.participantIds.find((id) => agents.some((agent) => agent.id === id))
    const firstAgent = agents.find((agent) => agent.id === participantId) || agents[0]
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
      mentions: firstAgent ? [{ agentId: firstAgent.id, agentName: firstAgent.name }] : [],
      createdAt: new Date().toISOString(),
    }
    const sent = send({
      type: 'send_message',
      data: {
        content,
        mentions: message.mentions || [],
        parentMessageId: null,
        clientMessageId,
      },
    })
    if (!sent) {
      setConversationError('WebSocket 尚未连接，消息未发送')
      return
    }
    addMessage(message)
  }

  return (
    <Layout
      left={
        <ConversationList
          activeId={activeId}
          agents={agents}
          conversations={conversations}
          onCreate={() => void handleCreateConversation()}
          onSelect={setActive}
        />
      }
      center={<ChatArea conversation={activeConversation} messages={messages} wsStatus={status} onSend={handleSend} />}
      right={<PreviewPanel />}
    />
  )
}

export default Workspace
