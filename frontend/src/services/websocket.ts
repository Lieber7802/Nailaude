type MessageHandler = (data: unknown) => void

export class WebSocketClient {
  private ws: WebSocket | null = null
  private handlers: Map<string, MessageHandler[]> = new Map()

  connect(conversationId: string) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const url = `${protocol}//${window.location.host}/ws/${conversationId}`
    this.ws = new WebSocket(url)

    this.ws.onmessage = (event) => {
      const msg = JSON.parse(event.data)
      const handlers = this.handlers.get(msg.type) || []
      handlers.forEach((h) => h(msg.data))
    }

    this.ws.onclose = () => {
      // TODO: reconnect logic
    }
  }

  disconnect() {
    this.ws?.close()
    this.ws = null
  }

  send(data: unknown) {
    this.ws?.send(JSON.stringify(data))
  }

  on(type: string, handler: MessageHandler) {
    const handlers = this.handlers.get(type) || []
    handlers.push(handler)
    this.handlers.set(type, handlers)
  }

  off(type: string, handler: MessageHandler) {
    const handlers = this.handlers.get(type) || []
    this.handlers.set(
      type,
      handlers.filter((h) => h !== handler)
    )
  }
}

export const wsClient = new WebSocketClient()
