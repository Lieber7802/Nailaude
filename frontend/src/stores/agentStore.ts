import { create } from 'zustand'

interface Agent {
  id: string
  name: string
  avatar: string
  description: string
  platformId: string
}

interface AgentState {
  agents: Agent[]
  setAgents: (agents: Agent[]) => void
  addAgent: (agent: Agent) => void
}

export const useAgentStore = create<AgentState>((set) => ({
  agents: [],
  setAgents: (agents) => set({ agents }),
  addAgent: (agent) =>
    set((state) => ({ agents: [...state.agents, agent] })),
}))
