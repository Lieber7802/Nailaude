import { create } from 'zustand'
import type { Message } from '../services/api'

interface MessageState {
  messagesByConversation: Record<string, Message[]>
  streamingContent: Record<string, string>
  setMessages: (conversationId: string, messages: Message[]) => void
  addMessage: (message: Message) => void
  replaceOptimisticMessage: (conversationId: string, clientMessageId: string, message: Message) => void
  appendStreamDelta: (conversationId: string, messageId: string, agentName: string, delta: string) => void
  finalizeStream: (conversationId: string, messageId: string, agentName: string) => void
  clearConversation: (conversationId: string) => void
}

export const useMessageStore = create<MessageState>((set, get) => ({
  messagesByConversation: {},
  streamingContent: {},
  setMessages: (conversationId, messages) =>
    set((state) => ({
      messagesByConversation: { ...state.messagesByConversation, [conversationId]: messages },
    })),
  addMessage: (message) =>
    set((state) => ({
      messagesByConversation: {
        ...state.messagesByConversation,
        [message.conversationId]: [...(state.messagesByConversation[message.conversationId] || []), message],
      },
    })),
  replaceOptimisticMessage: (conversationId, clientMessageId, message) =>
    set((state) => {
      const messages = state.messagesByConversation[conversationId] || []
      const optimisticIndex = messages.findIndex((item) => item.metadata?.clientMessageId === clientMessageId)
      if (optimisticIndex === -1) {
        return {
          messagesByConversation: {
            ...state.messagesByConversation,
            [conversationId]: [...messages, message],
          },
        }
      }

      return {
        messagesByConversation: {
          ...state.messagesByConversation,
          [conversationId]: messages.map((item, index) => (index === optimisticIndex ? message : item)),
        },
      }
    }),
  appendStreamDelta: (conversationId, messageId, agentName, delta) =>
    set((state) => {
      const nextContent = (state.streamingContent[messageId] || '') + delta
      const existingMessages = state.messagesByConversation[conversationId] || []
      const hasMessage = existingMessages.some((message) => message.id === messageId)
      const streamingMessage: Message = {
        id: messageId,
        conversationId,
        role: 'agent',
        agentId: null,
        agentName,
        content: nextContent,
        contentType: 'mixed',
        artifacts: [],
        parentMessageId: null,
        metadata: {},
        createdAt: new Date().toISOString(),
      }
      return {
        streamingContent: { ...state.streamingContent, [messageId]: nextContent },
        messagesByConversation: {
          ...state.messagesByConversation,
          [conversationId]: hasMessage
            ? existingMessages.map((message) =>
                message.id === messageId ? { ...message, content: nextContent, agentName } : message
              )
            : [...existingMessages, streamingMessage],
        },
      }
    }),
  finalizeStream: (conversationId, messageId, agentName) => {
    const content = get().streamingContent[messageId] || ''
    set((state) => {
      const rest = { ...state.streamingContent }
      delete rest[messageId]
      const messages = state.messagesByConversation[conversationId] || []
      return {
        streamingContent: rest,
        messagesByConversation: {
          ...state.messagesByConversation,
          [conversationId]: messages.map((message) =>
            message.id === messageId ? { ...message, content, agentName } : message
          ),
        },
      }
    })
  },
  clearConversation: (conversationId) =>
    set((state) => {
      const rest = { ...state.messagesByConversation }
      delete rest[conversationId]
      return { messagesByConversation: rest }
    }),
}))
