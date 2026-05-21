import { useEffect, useRef } from 'react'
import { wsClient } from '../services/websocket'

export function useWebSocket(conversationId: string | null) {
  const connectedRef = useRef(false)

  useEffect(() => {
    if (!conversationId) return

    wsClient.connect(conversationId)
    connectedRef.current = true

    return () => {
      wsClient.disconnect()
      connectedRef.current = false
    }
  }, [conversationId])

  return { send: wsClient.send.bind(wsClient) }
}
