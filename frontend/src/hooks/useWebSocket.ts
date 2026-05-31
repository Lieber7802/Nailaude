import { useEffect, useState } from 'react'
import { wsClient, type WSServerMessage } from '../services/websocket'
import { formatConversationLastMessage } from '../services/api'
import { useArtifactStore } from '../stores/artifactStore'
import { useConversationStore } from '../stores/conversationStore'
import { useMessageStore } from '../stores/messageStore'
import { useUIStore } from '../stores/uiStore'
import { useOrchestratorStore } from '../stores/orchestratorStore'
import { orchestratorApi } from '../services/orchestratorApi'

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
  const acceptSnapshot = useOrchestratorStore((state) => state.acceptSnapshot)
  const setInput = useOrchestratorStore((state) => state.setInput)
  const setApproval = useOrchestratorStore((state) => state.setApproval)
  const setTeamBoard = useOrchestratorStore((state) => state.setTeamBoard)
  const setProjectState = useOrchestratorStore((state) => state.setProjectState)

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
      if (!acceptSnapshot(conversationId, message.data)) return
      setOrchestratorStatus(conversationId, message.data.status, message.data.tasks)
      if (message.data.status !== 'awaiting_input') setInput(conversationId, undefined)
      if (message.data.status !== 'awaiting_approval') setApproval(conversationId, undefined)
    }
    const handleInputRequired = (message: Extract<WSServerMessage, { type: 'orchestrator_input_required' }>) => {
      setInput(conversationId, message.data)
    }
    const handleApprovalRequired = (message: Extract<WSServerMessage, { type: 'orchestrator_approval_required' }>) => {
      setApproval(conversationId, { runId: message.data.runId, reason: message.data.reason })
    }
    const handleTeamBoardUpdated = () => {
      void orchestratorApi.teamBoard(conversationId).then((board) => setTeamBoard(conversationId, board))
    }
    const handleProjectStateUpdated = () => {
      void orchestratorApi.projectState(conversationId).then((projectState) => setProjectState(conversationId, projectState))
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
    wsClient.on('orchestrator_input_required', handleInputRequired)
    wsClient.on('orchestrator_approval_required', handleApprovalRequired)
    wsClient.on('team_board_updated', handleTeamBoardUpdated)
    wsClient.on('project_state_updated', handleProjectStateUpdated)
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
      wsClient.off('orchestrator_input_required', handleInputRequired)
      wsClient.off('orchestrator_approval_required', handleApprovalRequired)
      wsClient.off('team_board_updated', handleTeamBoardUpdated)
      wsClient.off('project_state_updated', handleProjectStateUpdated)
      wsClient.off('error', handleError)
      wsClient.disconnect()
    }
  }, [
    addArtifact,
    acceptSnapshot,
    appendStreamDelta,
    clearThinkingAgent,
    clearThinkingAgents,
    conversationId,
    finalizeStream,
    replaceOptimisticMessage,
    resetRuntime,
    setOrchestratorStatus,
    setInput,
    setApproval,
    setProjectState,
    setRuntimeError,
    setTeamBoard,
    setThinkingAgent,
    touchConversation,
  ])

  return {
    status,
    send: wsClient.send.bind(wsClient),
  }
}
