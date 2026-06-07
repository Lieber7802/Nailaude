import { create } from 'zustand'
import type { Task } from '../services/api'
import type { OrchestratorRunStatus } from '../../../packages/shared/types'
import type { CollaborationTaskTiming } from '../utils/orchestratorUi'

export interface ConversationRuntimeState {
  error: string | null
  orchestratorStatus: OrchestratorRunStatus | null
  taskTimings: Record<string, CollaborationTaskTiming>
  tasks: Task[]
  thinkingAgents: string[]
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
  error: null,
  orchestratorStatus: null,
  taskTimings: {},
  tasks: [],
  thinkingAgents: [],
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
      const currentTiming = current.taskTimings[agentName]
      const nextTiming =
        currentTiming && !currentTiming.endedAt ? currentTiming : { startedAt: Date.now() }

      return {
        runtimeByConversation: {
          ...state.runtimeByConversation,
          [conversationId]: {
            ...current,
            taskTimings: {
              ...current.taskTimings,
              [agentName]: nextTiming,
            },
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
      const currentTiming = current.taskTimings[agentName]
      const taskTimings = currentTiming
        ? {
            ...current.taskTimings,
            [agentName]: {
              ...currentTiming,
              endedAt: currentTiming.endedAt ?? Date.now(),
            },
          }
        : current.taskTimings

      return {
        runtimeByConversation: {
          ...state.runtimeByConversation,
          [conversationId]: {
            ...current,
            taskTimings,
            thinkingAgents: current.thinkingAgents.filter((name) => name !== agentName),
          },
        },
      }
    }),
  clearThinkingAgents: (conversationId) =>
    set((state) => {
      const current = state.runtimeByConversation[conversationId] || emptyRuntime()
      const now = Date.now()
      const taskTimings = { ...current.taskTimings }

      for (const agentName of current.thinkingAgents) {
        const currentTiming = taskTimings[agentName]
        if (currentTiming) {
          taskTimings[agentName] = {
            ...currentTiming,
            endedAt: currentTiming.endedAt ?? now,
          }
        }
      }

      return {
        runtimeByConversation: {
          ...state.runtimeByConversation,
          [conversationId]: { ...current, taskTimings, thinkingAgents: [] },
        },
      }
    }),
  setOrchestratorStatus: (conversationId, status, tasks) =>
    set((state) => {
      const current = state.runtimeByConversation[conversationId] || emptyRuntime()
      const taskTimings = updateTaskTimings(current.taskTimings, tasks)

      return {
        runtimeByConversation: {
          ...state.runtimeByConversation,
          [conversationId]: {
            ...current,
            error: status === 'planning' ? null : current.error,
            orchestratorStatus: status,
            taskTimings,
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

const TERMINAL_TASK_STATUSES = new Set<Task['status']>(['completed', 'failed', 'blocked', 'cancelled'])

function updateTaskTimings(
  currentTimings: Record<string, CollaborationTaskTiming>,
  tasks: Task[]
): Record<string, CollaborationTaskTiming> {
  const now = Date.now()
  const taskTimings = { ...currentTimings }

  for (const task of tasks) {
    const currentTiming = taskTimings[task.agentName]

    if (task.status === 'running') {
      if (!currentTiming) continue
      taskTimings[task.agentName] = currentTiming.endedAt ? { startedAt: now } : currentTiming
      continue
    }

    if (TERMINAL_TASK_STATUSES.has(task.status)) {
      if (!currentTiming) continue
      taskTimings[task.agentName] = {
        startedAt: currentTiming.startedAt,
        endedAt: currentTiming?.endedAt ?? now,
      }
    }
  }

  return taskTimings
}
