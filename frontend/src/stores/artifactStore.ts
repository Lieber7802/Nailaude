import { create } from 'zustand'

interface Artifact {
  id: string
  messageId: string
  type: string
  title: string
}

interface ArtifactState {
  artifacts: Artifact[]
  activeArtifactId: string | null
  addArtifact: (artifact: Artifact) => void
  setActiveArtifact: (id: string | null) => void
}

export const useArtifactStore = create<ArtifactState>((set) => ({
  artifacts: [],
  activeArtifactId: null,
  addArtifact: (artifact) =>
    set((state) => ({ artifacts: [...state.artifacts, artifact] })),
  setActiveArtifact: (id) => set({ activeArtifactId: id }),
}))
