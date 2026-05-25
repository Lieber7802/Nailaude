import { create } from 'zustand'
import type { Conversation } from '../services/api'

interface ConversationState {
  conversations: Conversation[]
  activeId: string | null
  loading: boolean
  error: string | null
  setConversations: (conversations: Conversation[]) => void
  setActive: (id: string | null) => void
  addConversation: (conversation: Conversation) => void
  removeConversation: (id: string) => void
  touchConversation: (id: string, lastMessage: string, updatedAt?: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

export const useConversationStore = create<ConversationState>((set) => ({
  conversations: [],
  activeId: null,
  loading: false,
  error: null,
  setConversations: (conversations) =>
    set((state) => ({
      conversations,
      activeId: state.activeId ?? conversations[0]?.id ?? null,
    })),
  setActive: (id) => set({ activeId: id }),
  addConversation: (conversation) =>
    set((state) => ({
      conversations: [conversation, ...state.conversations.filter((item) => item.id !== conversation.id)],
      activeId: conversation.id,
    })),
  removeConversation: (id) =>
    set((state) => ({
      conversations: state.conversations.filter((conversation) => conversation.id !== id),
      activeId: state.activeId === id ? state.conversations.find((item) => item.id !== id)?.id ?? null : state.activeId,
    })),
  touchConversation: (id, lastMessage, updatedAt = new Date().toISOString()) =>
    set((state) => {
      const conversation = state.conversations.find((item) => item.id === id)
      if (!conversation) return {}
      const touchedConversation = { ...conversation, lastMessage, updatedAt }
      return {
        conversations: [touchedConversation, ...state.conversations.filter((item) => item.id !== id)],
      }
    }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}))
