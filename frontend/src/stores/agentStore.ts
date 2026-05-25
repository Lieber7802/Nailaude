import { create } from 'zustand'
import type { Agent } from '../services/api'

interface AgentState {
  agents: Agent[]
  loading: boolean
  error: string | null
  setAgents: (agents: Agent[]) => void
  addAgent: (agent: Agent) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

export const useAgentStore = create<AgentState>((set) => ({
  agents: [],
  loading: false,
  error: null,
  setAgents: (agents) => set({ agents }),
  addAgent: (agent) => set((state) => ({ agents: [...state.agents, agent] })),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}))
