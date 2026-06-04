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
  leftPaneWidth: number
  rightPaneWidth: number
  activePreviewTab: 'code' | 'preview' | 'diff'
  runtimeByConversation: Record<string, ConversationRuntimeState>
  toggleSidebar: () => void
  togglePreview: () => void
  setSidebarVisible: (visible: boolean) => void
  setPreviewVisible: (visible: boolean) => void
  setLeftPaneWidth: (width: number) => void
  setRightPaneWidth: (width: number) => void
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
  leftPaneWidth: 300,
  rightPaneWidth: 520,
  activePreviewTab: 'code',
  runtimeByConversation: {},
  toggleSidebar: () =>
    set((state) => ({ sidebarVisible: !state.sidebarVisible })),
  togglePreview: () =>
    set((state) => ({ previewVisible: !state.previewVisible })),
  setSidebarVisible: (visible) => set({ sidebarVisible: visible }),
  setPreviewVisible: (visible) => set({ previewVisible: visible }),
  setLeftPaneWidth: (width) => set({ leftPaneWidth: clamp(width, 240, 440) }),
  setRightPaneWidth: (width) => set({ rightPaneWidth: clamp(width, 340, 760) }),
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

const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, Math.round(value)))
