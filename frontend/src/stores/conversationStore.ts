import { create } from 'zustand'

interface Conversation {
  id: string
  title: string
  type: 'single' | 'group'
  updatedAt: string
}

interface ConversationState {
  conversations: Conversation[]
  activeId: string | null
  setActive: (id: string) => void
  addConversation: (conv: Conversation) => void
}

export const useConversationStore = create<ConversationState>((set) => ({
  conversations: [],
  activeId: null,
  setActive: (id) => set({ activeId: id }),
  addConversation: (conv) =>
    set((state) => ({ conversations: [...state.conversations, conv] })),
}))
