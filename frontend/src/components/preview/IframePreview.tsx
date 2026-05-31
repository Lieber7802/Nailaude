import { DesktopOutlined, MobileOutlined, TabletOutlined } from '@ant-design/icons'
import type { Artifact } from '../../services/api'

type PreviewViewport = 'desktop' | 'tablet' | 'mobile'

interface IframePreviewProps {
  artifact?: Artifact
  onViewportChange: (viewport: PreviewViewport) => void
  onZoomChange: (zoom: number) => void
  viewport: PreviewViewport
  zoom: number
}

const IframePreview = ({ artifact, onViewportChange, onZoomChange, viewport, zoom }: IframePreviewProps) => {
  const html = artifact?.files.find((file) => file.language === 'html' || file.name.endsWith('.html'))?.content

  if (!html && !artifact?.previewUrl) {
    return <div className="preview-empty">当前产出物暂不支持网页预览</div>
  }

  return (
    <div className="browser-preview">
      <div className="browser-preview__chrome">
        <strong>{artifact?.title || 'Preview'}</strong>
        <span>{artifact?.previewUrl || 'srcDoc'}</span>
      </div>
      <div className="browser-preview__stage">
        <div
          className={`browser-preview__viewport browser-preview__viewport--${viewport}`}
          style={{ transform: `scale(${zoom / 100})` }}
        >
          <iframe
            sandbox="allow-scripts allow-forms allow-same-origin"
            src={artifact?.previewUrl || undefined}
            srcDoc={artifact?.previewUrl ? undefined : html}
            title="Artifact preview"
          />
        </div>
      </div>
      <div className="preview-device-bar">
        <span className="viewport-switcher">
          <button
            aria-label="桌面预览"
            className={viewport === 'desktop' ? 'is-active' : ''}
            type="button"
            onClick={() => onViewportChange('desktop')}
          >
            <DesktopOutlined />
          </button>
          <button
            aria-label="平板预览"
            className={viewport === 'tablet' ? 'is-active' : ''}
            type="button"
            onClick={() => onViewportChange('tablet')}
          >
            <TabletOutlined />
          </button>
          <button
            aria-label="手机预览"
            className={viewport === 'mobile' ? 'is-active' : ''}
            type="button"
            onClick={() => onViewportChange('mobile')}
          >
            <MobileOutlined />
          </button>
        </span>
        <span className="zoom-switcher">
          <button disabled={zoom <= 75} type="button" onClick={() => onZoomChange(zoom - 25)}>
            -
          </button>
          <strong>{zoom}%</strong>
          <button disabled={zoom >= 125} type="button" onClick={() => onZoomChange(zoom + 25)}>
            +
          </button>
        </span>
      </div>
    </div>
  )
}

export default IframePreview
