export type PreviewViewport = 'desktop' | 'tablet' | 'mobile'

export interface ViewportOption {
  ariaLabel: string
  label: string
  viewport: PreviewViewport
}

export const VIEWPORT_OPTIONS: ViewportOption[] = [
  { ariaLabel: '切换到桌面预览', label: '桌面', viewport: 'desktop' },
  { ariaLabel: '切换到平板预览', label: '平板', viewport: 'tablet' },
  { ariaLabel: '切换到手机预览', label: '手机', viewport: 'mobile' },
]

export const PREVIEW_VIEWPORT_LABEL_HIDE_WIDTH = 430
export const PREVIEW_VIEWPORT_LABEL_CLASS = 'viewport-switcher__label'

export const FULLSCREEN_ACTIONS = {
  enter: { ariaLabel: '全屏预览', label: '全屏预览' },
  exit: { ariaLabel: '退出全屏预览', label: '退出全屏' },
} as const

export const PREVIEW_ZOOM = {
  min: 25,
  max: 300,
  step: 10,
} as const

export function clampPreviewZoom(zoom: number): number {
  return Math.min(PREVIEW_ZOOM.max, Math.max(PREVIEW_ZOOM.min, Math.round(zoom)))
}
