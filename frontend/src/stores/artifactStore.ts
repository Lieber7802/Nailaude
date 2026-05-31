import { create } from 'zustand'
import type { Artifact, Message } from '../services/api'

interface ArtifactState {
  artifactsByMessage: Record<string, Artifact[]>
  activeArtifact: Artifact | null
  activeArtifactId: string | null
  openRevision: number
  addArtifact: (messageId: string, artifact: Artifact) => void
  openArtifact: (artifact: Artifact) => void
  setArtifactsFromMessages: (messages: Message[]) => void
  setActiveArtifact: (id: string | null) => void
}

export const useArtifactStore = create<ArtifactState>((set) => ({
  artifactsByMessage: {},
  activeArtifact: null,
  activeArtifactId: null,
  openRevision: 0,
  addArtifact: (messageId, artifact) =>
    set((state) => ({
      artifactsByMessage: {
        ...state.artifactsByMessage,
        [messageId]: [...(state.artifactsByMessage[messageId] || []), artifact],
      },
      activeArtifact: artifact,
      activeArtifactId: artifact.id,
      openRevision: state.openRevision + 1,
    })),
  openArtifact: (artifact) =>
    set((state) => {
      const messageArtifacts = state.artifactsByMessage[artifact.messageId] || []
      const exists = messageArtifacts.some((item) => item.id === artifact.id)
      return {
        artifactsByMessage: exists
          ? state.artifactsByMessage
          : {
              ...state.artifactsByMessage,
              [artifact.messageId]: [...messageArtifacts, artifact],
            },
        activeArtifact: artifact,
        activeArtifactId: artifact.id,
        openRevision: state.openRevision + 1,
      }
    }),
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
      const activeArtifact = activeArtifactExists
        ? artifacts.find((artifact) => artifact.id === state.activeArtifactId) || null
        : artifacts[0] || null
      return {
        artifactsByMessage,
        activeArtifact,
        activeArtifactId: activeArtifact?.id || null,
      }
    }),
  setActiveArtifact: (id) =>
    set((state) => {
      const activeArtifact = Object.values(state.artifactsByMessage)
        .flat()
        .find((artifact) => artifact.id === id)
      return { activeArtifact: activeArtifact || null, activeArtifactId: id }
    }),
}))
