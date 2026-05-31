import { create } from 'zustand'
import type { Task } from '../services/api'
import type { OrchestratorRunStatus } from '../../../packages/shared/types'

export interface ConversationRuntimeState {
  thinkingAgents: string[]
  orchestratorStatus: OrchestratorRunStatus | null
  tasks: Task[]
  error: string | null
}

interface UIState {
  sidebarVisible: boolean
  previewVisible: boolean
  activePreviewTab: 'code' | 'preview' | 'diff'
  runtimeByConversation: Record<string, ConversationRuntimeState>
  toggleSidebar: () => void
  togglePreview: () => void
  setPreviewTab: (tab: 'code' | 'preview' | 'diff') => void
  setThinkingAgent: (conversationId: string, agentName: string) => void
  clearThinkingAgent: (conversationId: string, agentName: string) => void
  clearThinkingAgents: (conversationId: string) => void
  setOrchestratorStatus: (
    conversationId: string,
    status: ConversationRuntimeState['orchestratorStatus'],
    tasks: Task[]
  ) => void
  setRuntimeError: (conversationId: string, error: string | null) => void
  resetRuntime: (conversationId: string) => void
}

const emptyRuntime = (): ConversationRuntimeState => ({
  thinkingAgents: [],
  orchestratorStatus: null,
  tasks: [],
  error: null,
})

export const useUIStore = create<UIState>((set) => ({
  sidebarVisible: true,
  previewVisible: true,
  activePreviewTab: 'code',
  runtimeByConversation: {},
  toggleSidebar: () =>
    set((state) => ({ sidebarVisible: !state.sidebarVisible })),
  togglePreview: () =>
    set((state) => ({ previewVisible: !state.previewVisible })),
  setPreviewTab: (tab) => set({ activePreviewTab: tab }),
  setThinkingAgent: (conversationId, agentName) =>
    set((state) => {
      const current = state.runtimeByConversation[conversationId] || emptyRuntime()
      return {
        runtimeByConversation: {
          ...state.runtimeByConversation,
          [conversationId]: {
            ...current,
            thinkingAgents: current.thinkingAgents.includes(agentName)
              ? current.thinkingAgents
              : [...current.thinkingAgents, agentName],
          },
        },
      }
    }),
  clearThinkingAgent: (conversationId, agentName) =>
    set((state) => {
      const current = state.runtimeByConversation[conversationId] || emptyRuntime()
      return {
        runtimeByConversation: {
          ...state.runtimeByConversation,
          [conversationId]: {
            ...current,
            thinkingAgents: current.thinkingAgents.filter((name) => name !== agentName),
          },
        },
      }
    }),
  clearThinkingAgents: (conversationId) =>
    set((state) => {
      const current = state.runtimeByConversation[conversationId] || emptyRuntime()
      return {
        runtimeByConversation: {
          ...state.runtimeByConversation,
          [conversationId]: { ...current, thinkingAgents: [] },
        },
      }
    }),
  setOrchestratorStatus: (conversationId, status, tasks) =>
    set((state) => {
      const current = state.runtimeByConversation[conversationId] || emptyRuntime()
      return {
        runtimeByConversation: {
          ...state.runtimeByConversation,
          [conversationId]: {
            ...current,
            error: status === 'planning' ? null : current.error,
            orchestratorStatus: status,
            tasks,
          },
        },
      }
    }),
  setRuntimeError: (conversationId, error) =>
    set((state) => {
      const current = state.runtimeByConversation[conversationId] || emptyRuntime()
      return {
        runtimeByConversation: {
          ...state.runtimeByConversation,
          [conversationId]: { ...current, error },
        },
      }
    }),
  resetRuntime: (conversationId) =>
    set((state) => ({
      runtimeByConversation: {
        ...state.runtimeByConversation,
        [conversationId]: emptyRuntime(),
      },
    })),
}))
