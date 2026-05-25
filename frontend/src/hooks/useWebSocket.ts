import { useEffect, useState } from 'react'
import { wsClient, type WSServerMessage } from '../services/websocket'
import { formatConversationLastMessage } from '../services/api'
import { useArtifactStore } from '../stores/artifactStore'
import { useConversationStore } from '../stores/conversationStore'
import { useMessageStore } from '../stores/messageStore'
import { useUIStore } from '../stores/uiStore'

export function useWebSocket(conversationId: string | null) {
  const [status, setStatus] = useState<'idle' | 'connecting' | 'open' | 'closed' | 'error'>('idle')
  const appendStreamDelta = useMessageStore((state) => state.appendStreamDelta)
  const finalizeStream = useMessageStore((state) => state.finalizeStream)
  const replaceOptimisticMessage = useMessageStore((state) => state.replaceOptimisticMessage)
  const touchConversation = useConversationStore((state) => state.touchConversation)
  const addArtifact = useArtifactStore((state) => state.addArtifact)
  const setThinkingAgent = useUIStore((state) => state.setThinkingAgent)
  const clearThinkingAgent = useUIStore((state) => state.clearThinkingAgent)
  const clearThinkingAgents = useUIStore((state) => state.clearThinkingAgents)
  const setOrchestratorStatus = useUIStore((state) => state.setOrchestratorStatus)
  const setRuntimeError = useUIStore((state) => state.setRuntimeError)
  const resetRuntime = useUIStore((state) => state.resetRuntime)

  useEffect(() => {
    if (!conversationId) return

    const handleStatus = (nextStatus: 'idle' | 'connecting' | 'open' | 'closed' | 'error') => setStatus(nextStatus)
    resetRuntime(conversationId)
    const handleUserMessage = (message: Extract<WSServerMessage, { type: 'user_message' }>) => {
      const { clientMessageId, ...persistedMessage } = message.data
      setRuntimeError(conversationId, null)
      if (clientMessageId) {
        replaceOptimisticMessage(conversationId, clientMessageId, persistedMessage)
      }
      touchConversation(conversationId, formatConversationLastMessage('你', persistedMessage.content), persistedMessage.createdAt)
    }
    const handleThinking = (message: Extract<WSServerMessage, { type: 'agent_thinking' }>) => {
      setThinkingAgent(conversationId, message.data.agentName)
    }
    const handleDelta = (message: Extract<WSServerMessage, { type: 'text_delta' }>) => {
      appendStreamDelta(conversationId, message.data.messageId, message.data.agentName, message.data.delta)
    }
    const handleDone = (message: Extract<WSServerMessage, { type: 'message_done' }>) => {
      const content = useMessageStore.getState().streamingContent[message.data.messageId] || ''
      finalizeStream(conversationId, message.data.messageId, message.data.agentName)
      clearThinkingAgent(conversationId, message.data.agentName)
      touchConversation(conversationId, formatConversationLastMessage(message.data.agentName, content))
    }
    const handleArtifact = (message: Extract<WSServerMessage, { type: 'artifact' }>) => {
      addArtifact(message.data.messageId, message.data.artifact)
    }
    const handleOrchestratorStatus = (message: Extract<WSServerMessage, { type: 'orchestrator_status' }>) => {
      setOrchestratorStatus(conversationId, message.data.status, message.data.tasks)
    }
    const handleError = (message: Extract<WSServerMessage, { type: 'error' }>) => {
      setRuntimeError(conversationId, message.data.error)
      clearThinkingAgents(conversationId)
    }

    wsClient.onStatus(handleStatus)
    wsClient.on('user_message', handleUserMessage)
    wsClient.on('agent_thinking', handleThinking)
    wsClient.on('text_delta', handleDelta)
    wsClient.on('message_done', handleDone)
    wsClient.on('artifact', handleArtifact)
    wsClient.on('orchestrator_status', handleOrchestratorStatus)
    wsClient.on('error', handleError)
    wsClient.connect(conversationId)

    return () => {
      wsClient.offStatus(handleStatus)
      wsClient.off('user_message', handleUserMessage)
      wsClient.off('agent_thinking', handleThinking)
      wsClient.off('text_delta', handleDelta)
      wsClient.off('message_done', handleDone)
      wsClient.off('artifact', handleArtifact)
      wsClient.off('orchestrator_status', handleOrchestratorStatus)
      wsClient.off('error', handleError)
      wsClient.disconnect()
    }
  }, [
    addArtifact,
    appendStreamDelta,
    clearThinkingAgent,
    clearThinkingAgents,
    conversationId,
    finalizeStream,
    replaceOptimisticMessage,
    resetRuntime,
    setOrchestratorStatus,
    setRuntimeError,
    setThinkingAgent,
    touchConversation,
  ])

  return {
    status,
    send: wsClient.send.bind(wsClient),
  }
}
