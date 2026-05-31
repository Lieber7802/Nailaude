import type { SendMessageDTO, WSClientMessage, WSServerMessage } from '../../../packages/shared/types'
import { reconnectDelay } from './orchestratorLogic.mjs'

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
  private conversationId: string | null = null
  private reconnectAttempt = 0
  private reconnectTimer: number | null = null
  private manuallyDisconnected = false

  connect(conversationId: string) {
    const resetAttempts = this.conversationId !== conversationId || this.manuallyDisconnected
    this.disconnect(false)
    this.conversationId = conversationId
    this.manuallyDisconnected = false
    if (resetAttempts) this.reconnectAttempt = 0
    this.emitStatus('connecting')
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const url = `${protocol}//${window.location.host}/ws/${conversationId}`
    const socket = new WebSocket(url)
    this.ws = socket

    socket.onopen = () => {
      if (this.ws === socket) {
        this.reconnectAttempt = 0
        this.emitStatus('open')
      }
    }
    socket.onerror = () => {
      if (this.ws === socket) this.emitStatus('error')
    }
    socket.onclose = () => {
      if (this.ws === socket) {
        this.ws = null
        this.emitStatus('closed')
        this.scheduleReconnect()
      }
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

  disconnect(manual = true) {
    if (manual) {
      this.manuallyDisconnected = true
      this.conversationId = null
    }
    if (this.reconnectTimer !== null) {
      window.clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
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

  private scheduleReconnect() {
    if (this.manuallyDisconnected || !this.conversationId || this.reconnectAttempt >= 5) return
    const conversationId = this.conversationId
    const delay = reconnectDelay(this.reconnectAttempt)
    this.reconnectAttempt += 1
    this.reconnectTimer = window.setTimeout(() => {
      this.reconnectTimer = null
      if (!this.manuallyDisconnected && this.conversationId === conversationId) this.connect(conversationId)
    }, delay)
  }
}

export const wsClient = new WebSocketClient()
