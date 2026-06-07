import { DesktopOutlined, MobileOutlined, TabletOutlined } from '@ant-design/icons'
import type { CSSProperties } from 'react'
import type { Artifact } from '../../services/api'
import { getIframePreviewSource } from '../../utils/markdownPreview'
import {
  PREVIEW_VIEWPORT_LABEL_CLASS,
  PREVIEW_ZOOM,
  VIEWPORT_OPTIONS,
  type PreviewViewport,
} from '../../utils/previewControls'

interface IframePreviewProps {
  artifact?: Artifact
  onViewportChange: (viewport: PreviewViewport) => void
  onZoomChange: (zoom: number) => void
  viewport: PreviewViewport
  zoom: number
}

const IframePreview = ({ artifact, onViewportChange, onZoomChange, viewport, zoom }: IframePreviewProps) => {
  const { html, previewUrl } = getIframePreviewSource(artifact)

  if (!html && !previewUrl) {
    return <div className="preview-empty">选择一个网页产物后在此预览</div>
  }

  return (
    <div className="browser-preview" style={{ '--preview-scale': zoom / 100 } as CSSProperties}>
      <div className="browser-preview__chrome">
        <strong>{artifact?.title || 'Preview'}</strong>
        <span>{previewUrl || artifact?.files[0]?.name || 'srcDoc'}</span>
      </div>
      <div className="browser-preview__stage">
        <div className={`browser-preview__viewport browser-preview__viewport--${viewport}`}>
          <iframe
            sandbox="allow-scripts allow-forms allow-same-origin"
            src={previewUrl}
            srcDoc={html || undefined}
            title="Artifact preview"
          />
        </div>
      </div>
      <div className="preview-device-bar">
        <div aria-label="预览尺寸" className="viewport-switcher" role="group">
          {VIEWPORT_OPTIONS.map((option) => (
            <button
              aria-label={option.ariaLabel}
              className={viewport === option.viewport ? 'is-active' : ''}
              key={option.viewport}
              title={option.ariaLabel}
              type="button"
              onClick={() => onViewportChange(option.viewport)}
            >
              {iconForViewport(option.viewport)}
              <span className={PREVIEW_VIEWPORT_LABEL_CLASS}>{option.label}</span>
            </button>
          ))}
        </div>
        <div aria-label="预览缩放" className="zoom-switcher" role="group">
          <button disabled={zoom <= PREVIEW_ZOOM.min} type="button" onClick={() => onZoomChange(zoom - PREVIEW_ZOOM.step)}>
            -
          </button>
          <strong>{zoom}%</strong>
          <input
            aria-label="调整预览缩放"
            max={PREVIEW_ZOOM.max}
            min={PREVIEW_ZOOM.min}
            step={PREVIEW_ZOOM.step}
            type="range"
            value={zoom}
            onChange={(event) => onZoomChange(Number(event.target.value))}
          />
          <button disabled={zoom >= PREVIEW_ZOOM.max} type="button" onClick={() => onZoomChange(zoom + PREVIEW_ZOOM.step)}>
            +
          </button>
        </div>
      </div>
    </div>
  )
}

const iconForViewport = (viewport: PreviewViewport) => {
  if (viewport === 'tablet') return <TabletOutlined />
  if (viewport === 'mobile') return <MobileOutlined />
  return <DesktopOutlined />
}

export default IframePreview
