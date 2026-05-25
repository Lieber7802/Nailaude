import { useEffect, useState } from 'react'
import { wsClient, type WSServerMessage } from '../services/websocket'
import { useArtifactStore } from '../stores/artifactStore'
import { useMessageStore } from '../stores/messageStore'

export function useWebSocket(conversationId: string | null) {
  const [status, setStatus] = useState<'idle' | 'connecting' | 'open' | 'closed' | 'error'>('idle')
  const appendStreamDelta = useMessageStore((state) => state.appendStreamDelta)
  const finalizeStream = useMessageStore((state) => state.finalizeStream)
  const replaceOptimisticMessage = useMessageStore((state) => state.replaceOptimisticMessage)
  const addArtifact = useArtifactStore((state) => state.addArtifact)

  useEffect(() => {
    if (!conversationId) return

    const handleStatus = (nextStatus: 'idle' | 'connecting' | 'open' | 'closed' | 'error') => setStatus(nextStatus)
    const handleUserMessage = (message: Extract<WSServerMessage, { type: 'user_message' }>) => {
      const { clientMessageId, ...persistedMessage } = message.data
      if (clientMessageId) {
        replaceOptimisticMessage(conversationId, clientMessageId, persistedMessage)
      }
    }
    const handleDelta = (message: Extract<WSServerMessage, { type: 'text_delta' }>) => {
      appendStreamDelta(conversationId, message.data.messageId, message.data.agentName, message.data.delta)
    }
    const handleDone = (message: Extract<WSServerMessage, { type: 'message_done' }>) => {
      finalizeStream(conversationId, message.data.messageId, message.data.agentName)
    }
    const handleArtifact = (message: Extract<WSServerMessage, { type: 'artifact' }>) => {
      addArtifact(message.data.messageId, message.data.artifact)
    }

    wsClient.onStatus(handleStatus)
    wsClient.on('user_message', handleUserMessage)
    wsClient.on('text_delta', handleDelta)
    wsClient.on('message_done', handleDone)
    wsClient.on('artifact', handleArtifact)
    wsClient.connect(conversationId)

    return () => {
      wsClient.offStatus(handleStatus)
      wsClient.off('user_message', handleUserMessage)
      wsClient.off('text_delta', handleDelta)
      wsClient.off('message_done', handleDone)
      wsClient.off('artifact', handleArtifact)
      wsClient.disconnect()
    }
  }, [addArtifact, appendStreamDelta, conversationId, finalizeStream, replaceOptimisticMessage])

  return {
    status,
    send: wsClient.send.bind(wsClient),
  }
}
