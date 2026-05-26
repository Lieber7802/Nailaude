import type { SendMessageDTO, WSClientMessage, WSServerMessage } from '../../../packages/shared/types'

export type { WSServerMessage }
export type WSOutboundMessage =
  | WSClientMessage
  | {
      type: 'send_message'
      data: SendMessageDTO & { clientMessageId?: string }
    }

type MessageHandler<T extends WSServerMessage = WSServerMessage> = (message: T) => void
type StatusHandler = (status: 'idle' | 'connecting' | 'open' | 'closed' | 'error') => void

export class WebSocketClient {
  private ws: WebSocket | null = null
  private handlers: Map<string, MessageHandler[]> = new Map()
  private statusHandlers: StatusHandler[] = []

  connect(conversationId: string) {
    this.disconnect()
    this.emitStatus('connecting')
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const url = `${protocol}//${window.location.host}/ws/${conversationId}`
    const socket = new WebSocket(url)
    this.ws = socket

    socket.onopen = () => {
      if (this.ws === socket) this.emitStatus('open')
    }
    socket.onerror = () => {
      if (this.ws === socket) this.emitStatus('error')
    }
    socket.onclose = () => {
      if (this.ws === socket) this.emitStatus('closed')
    }
    socket.onmessage = (event) => {
      if (this.ws !== socket) return
      let message: WSServerMessage
      try {
        message = JSON.parse(event.data) as WSServerMessage
      } catch {
        this.emitStatus('error')
        return
      }
      const handlers = this.handlers.get(message.type) || []
      handlers.forEach((handler) => handler(message))
    }
  }

  disconnect() {
    const socket = this.ws
    this.ws = null
    socket?.close()
    this.emitStatus('idle')
  }

  send(data: WSOutboundMessage): boolean {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
      return true
    }
    return false
  }

  on<T extends WSServerMessage>(type: T['type'], handler: MessageHandler<T>) {
    const handlers = this.handlers.get(type) || []
    handlers.push(handler as MessageHandler)
    this.handlers.set(type, handlers)
  }

  off<T extends WSServerMessage>(type: T['type'], handler: MessageHandler<T>) {
    const handlers = this.handlers.get(type) || []
    this.handlers.set(
      type,
      handlers.filter((item) => item !== handler)
    )
  }

  onStatus(handler: StatusHandler) {
    this.statusHandlers.push(handler)
  }

  offStatus(handler: StatusHandler) {
    this.statusHandlers = this.statusHandlers.filter((item) => item !== handler)
  }

  private emitStatus(status: 'idle' | 'connecting' | 'open' | 'closed' | 'error') {
    this.statusHandlers.forEach((handler) => handler(status))
  }
}

export const wsClient = new WebSocketClient()
