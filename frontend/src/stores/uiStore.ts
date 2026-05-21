import { create } from 'zustand'

interface UIState {
  sidebarVisible: boolean
  previewVisible: boolean
  activePreviewTab: 'code' | 'preview' | 'diff'
  toggleSidebar: () => void
  togglePreview: () => void
  setPreviewTab: (tab: 'code' | 'preview' | 'diff') => void
}

export const useUIStore = create<UIState>((set) => ({
  sidebarVisible: true,
  previewVisible: true,
  activePreviewTab: 'code',
  toggleSidebar: () =>
    set((state) => ({ sidebarVisible: !state.sidebarVisible })),
  togglePreview: () =>
    set((state) => ({ previewVisible: !state.previewVisible })),
  setPreviewTab: (tab) => set({ activePreviewTab: tab }),
}))
