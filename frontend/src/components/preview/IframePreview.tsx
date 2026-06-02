import { DesktopOutlined, MobileOutlined, TabletOutlined } from '@ant-design/icons'
import type { Artifact } from '../../services/api'
import { isHtmlFile } from '../../utils/markdownPreview'
import { VIEWPORT_OPTIONS, type PreviewViewport } from '../../utils/previewControls'

interface IframePreviewProps {
  artifact?: Artifact
  onViewportChange: (viewport: PreviewViewport) => void
  onZoomChange: (zoom: number) => void
  viewport: PreviewViewport
  zoom: number
}

const IframePreview = ({ artifact, onViewportChange, onZoomChange, viewport, zoom }: IframePreviewProps) => {
  const html = artifact?.files.find((file) => isHtmlFile(file))?.content
  const previewUrl = html ? undefined : artifact?.previewUrl || undefined

  if (!html && !previewUrl) {
    return <div className="preview-empty">当前产出物暂不支持网页预览</div>
  }

  return (
    <div className="browser-preview">
      <div className="browser-preview__chrome">
        <strong>{artifact?.title || 'Preview'}</strong>
        <span>{previewUrl || artifact?.files[0]?.name || 'srcDoc'}</span>
      </div>
      <div className="browser-preview__stage">
        <div
          className={`browser-preview__viewport browser-preview__viewport--${viewport}`}
          style={{ transform: `scale(${zoom / 100})` }}
        >
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
              <span>{option.label}</span>
            </button>
          ))}
        </div>
        <div aria-label="预览缩放" className="zoom-switcher" role="group">
          <button disabled={zoom <= 75} type="button" onClick={() => onZoomChange(zoom - 25)}>
            -
          </button>
          <strong>{zoom}%</strong>
          <button disabled={zoom >= 125} type="button" onClick={() => onZoomChange(zoom + 25)}>
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
