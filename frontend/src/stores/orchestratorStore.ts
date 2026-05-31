import { create } from 'zustand'
import type {
  PlannerResult,
  ProjectState,
  TeamBoard,
  WSOrchestratorStatus,
} from '../../../packages/shared/types'
import { shouldAcceptSnapshot } from '../services/orchestratorLogic.mjs'

type InputRequirement = Extract<PlannerResult, { status: 'needs_clarification' | 'capability_gap' }>

interface ApprovalRequirement {
  runId: string
  reason: string
}

interface OrchestratorState {
  snapshots: Record<string, WSOrchestratorStatus>
  inputs: Record<string, { runId: string; result: InputRequirement } | undefined>
  approvals: Record<string, ApprovalRequirement | undefined>
  teamBoards: Record<string, TeamBoard | undefined>
  projectStates: Record<string, ProjectState | undefined>
  acceptSnapshot: (conversationId: string, snapshot: WSOrchestratorStatus) => boolean
  setInput: (conversationId: string, input?: { runId: string; result: InputRequirement }) => void
  setApproval: (conversationId: string, approval?: ApprovalRequirement) => void
  setTeamBoard: (conversationId: string, board: TeamBoard) => void
  setProjectState: (conversationId: string, projectState: ProjectState) => void
}

export function mergeOrchestratorSnapshot(
  current: WSOrchestratorStatus | undefined,
  incoming: WSOrchestratorStatus
): WSOrchestratorStatus {
  if (!shouldAcceptSnapshot(current, incoming)) return current ?? incoming
  return incoming
}

export const useOrchestratorStore = create<OrchestratorState>((set) => ({
  snapshots: {},
  inputs: {},
  approvals: {},
  teamBoards: {},
  projectStates: {},
  acceptSnapshot: (conversationId, snapshot) => {
    let accepted = false
    set((state) => {
      const current = state.snapshots[conversationId]
      const next = mergeOrchestratorSnapshot(current, snapshot)
      accepted = next !== current
      return accepted
        ? { snapshots: { ...state.snapshots, [conversationId]: next } }
        : state
    })
    return accepted
  },
  setInput: (conversationId, input) =>
    set((state) => ({ inputs: { ...state.inputs, [conversationId]: input } })),
  setApproval: (conversationId, approval) =>
    set((state) => ({ approvals: { ...state.approvals, [conversationId]: approval } })),
  setTeamBoard: (conversationId, board) =>
    set((state) => ({ teamBoards: { ...state.teamBoards, [conversationId]: board } })),
  setProjectState: (conversationId, projectState) =>
    set((state) => ({ projectStates: { ...state.projectStates, [conversationId]: projectState } })),
}))
