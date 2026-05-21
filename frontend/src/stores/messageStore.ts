import { create } from 'zustand'

interface Message {
  id: string
  conversationId: string
  role: string
  content: string
  createdAt: string
}

interface MessageState {
  messages: Message[]
  streamingContent: Record<string, string>
  addMessage: (msg: Message) => void
  appendStreamDelta: (messageId: string, delta: string) => void
  clearStream: (messageId: string) => void
}

export const useMessageStore = create<MessageState>((set) => ({
  messages: [],
  streamingContent: {},
  addMessage: (msg) =>
    set((state) => ({ messages: [...state.messages, msg] })),
  appendStreamDelta: (messageId, delta) =>
    set((state) => ({
      streamingContent: {
        ...state.streamingContent,
        [messageId]: (state.streamingContent[messageId] || '') + delta,
      },
    })),
  clearStream: (messageId) =>
    set((state) => {
      const { [messageId]: _, ...rest } = state.streamingContent
      return { streamingContent: rest }
    }),
}))
