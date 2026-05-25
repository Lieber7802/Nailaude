import { create } from 'zustand'
import type { Artifact, Message } from '../services/api'

interface ArtifactState {
  artifactsByMessage: Record<string, Artifact[]>
  activeArtifactId: string | null
  addArtifact: (messageId: string, artifact: Artifact) => void
  setArtifactsFromMessages: (messages: Message[]) => void
  setActiveArtifact: (id: string | null) => void
}

export const useArtifactStore = create<ArtifactState>((set) => ({
  artifactsByMessage: {},
  activeArtifactId: null,
  addArtifact: (messageId, artifact) =>
    set((state) => ({
      artifactsByMessage: {
        ...state.artifactsByMessage,
        [messageId]: [...(state.artifactsByMessage[messageId] || []), artifact],
      },
      activeArtifactId: artifact.id,
    })),
  setArtifactsFromMessages: (messages) =>
    set((state) => {
      const artifactsByMessage: Record<string, Artifact[]> = {}
      for (const message of messages) {
        if (message.artifacts.length > 0) {
          artifactsByMessage[message.id] = message.artifacts
        }
      }
      const artifacts = Object.values(artifactsByMessage).flat()
      const activeArtifactExists = artifacts.some((artifact) => artifact.id === state.activeArtifactId)
      return {
        artifactsByMessage,
        activeArtifactId: activeArtifactExists ? state.activeArtifactId : artifacts[0]?.id || null,
      }
    }),
  setActiveArtifact: (id) => set({ activeArtifactId: id }),
}))
