import {
  CodeOutlined,
  DesktopOutlined,
  DiffOutlined,
  ExpandOutlined,
  FileTextOutlined,
  MobileOutlined,
  TabletOutlined,
} from '@ant-design/icons'
import { useMemo, useState } from 'react'
import type { Artifact } from '../../services/api'
import { useArtifactStore } from '../../stores/artifactStore'

type PreviewTab = 'outputs' | 'preview' | 'changes'
type PreviewViewport = 'desktop' | 'tablet' | 'mobile'

const MIN_ZOOM = 75
const MAX_ZOOM = 125
const ZOOM_STEP = 25

const PreviewPanel = () => {
  const [activeTab, setActiveTab] = useState<PreviewTab>('preview')
  const [viewport, setViewport] = useState<PreviewViewport>('desktop')
  const [zoom, setZoom] = useState(100)
  const artifactsByMessage = useArtifactStore((state) => state.artifactsByMessage)
  const activeArtifactId = useArtifactStore((state) => state.activeArtifactId)
  const setActiveArtifact = useArtifactStore((state) => state.setActiveArtifact)
  const artifacts = useMemo(() => Object.values(artifactsByMessage).flat(), [artifactsByMessage])
  const activeArtifact = artifacts.find((artifact) => artifact.id === activeArtifactId) || artifacts[0]
  const firstFile = activeArtifact?.files[0]
  const previewHtml = getPreviewHtml(activeArtifact)

  return (
    <div className="preview-panel">
      <div className="preview-panel__header">
        <div className="preview-tabs">
          <button
            className={activeTab === 'outputs' ? 'is-active' : ''}
            type="button"
            onClick={() => setActiveTab('outputs')}
          >
            产出物
          </button>
          <button
            className={activeTab === 'preview' ? 'is-active' : ''}
            type="button"
            onClick={() => setActiveTab('preview')}
          >
            预览
          </button>
          <button
            className={activeTab === 'changes' ? 'is-active' : ''}
            type="button"
            onClick={() => setActiveTab('changes')}
          >
            变更
          </button>
        </div>
        <div className="preview-toolbar">
          <button type="button">
            <FileTextOutlined />
            {firstFile?.name || '暂无文件'}
          </button>
          <button aria-label="展开预览" type="button">
            <ExpandOutlined />
          </button>
        </div>
      </div>

      <div className="preview-panel__body">
        {activeTab === 'outputs' && (
          <OutputsTab artifacts={artifacts} activeArtifact={activeArtifact} onSelect={setActiveArtifact} />
        )}
        {activeTab === 'preview' && (
          <PreviewTabContent
            html={previewHtml}
            viewport={viewport}
            zoom={zoom}
            onViewportChange={setViewport}
            onZoomChange={(nextZoom) => setZoom(Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, nextZoom)))}
          />
        )}
        {activeTab === 'changes' && <ChangesTab artifact={activeArtifact} />}
      </div>
    </div>
  )
}

const OutputsTab = ({
  activeArtifact,
  artifacts,
  onSelect,
}: {
  activeArtifact?: Artifact
  artifacts: Artifact[]
  onSelect: (id: string | null) => void
}) => {
  if (artifacts.length === 0) {
    return <div className="preview-empty">等待 Agent 生成产出物</div>
  }

  return (
    <div className="output-list">
      {artifacts.map((artifact) => {
        const file = artifact.files[0]
        return (
          <button
            className={artifact.id === activeArtifact?.id ? 'output-row is-active' : 'output-row'}
            key={artifact.id}
            type="button"
            onClick={() => onSelect(artifact.id)}
          >
            <span className="output-row__icon">
              <CodeOutlined />
            </span>
            <span>
              <strong>{artifact.title}</strong>
              <small>
                {file?.language?.toUpperCase() || artifact.type} · {formatBytes(file?.content.length || 0)}
              </small>
            </span>
          </button>
        )
      })}
    </div>
  )
}

const PreviewTabContent = ({
  html,
  onViewportChange,
  onZoomChange,
  viewport,
  zoom,
}: {
  html: string | null
  onViewportChange: (viewport: PreviewViewport) => void
  onZoomChange: (zoom: number) => void
  viewport: PreviewViewport
  zoom: number
}) => {
  if (!html) {
    return <div className="preview-empty">当前产出物暂不支持网页预览</div>
  }

  return (
    <div className="browser-preview">
      <div className="browser-preview__chrome">
        <strong>AgentHub Mock</strong>
        <nav>
          <span>首页</span>
          <span>功能</span>
          <span>关于</span>
        </nav>
      </div>
      <div className="browser-preview__stage">
        <div
          className={`browser-preview__viewport browser-preview__viewport--${viewport}`}
          style={{ transform: `scale(${zoom / 100})` }}
        >
          <iframe sandbox="" srcDoc={html} title="Artifact preview" />
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
          <button disabled={zoom <= MIN_ZOOM} type="button" onClick={() => onZoomChange(zoom - ZOOM_STEP)}>
            −
          </button>
          <strong>{zoom}%</strong>
          <button disabled={zoom >= MAX_ZOOM} type="button" onClick={() => onZoomChange(zoom + ZOOM_STEP)}>
            +
          </button>
        </span>
      </div>
    </div>
  )
}

const ChangesTab = ({ artifact }: { artifact?: Artifact }) => {
  if (!artifact?.diffData) {
    return (
      <div className="preview-empty">
        <DiffOutlined />
        当前没有可展示的变更对比
      </div>
    )
  }

  return (
    <pre className="changes-view">
      {artifact.diffData.hunks.map((hunk) => hunk.content).join('\n')}
    </pre>
  )
}

const getPreviewHtml = (artifact?: Artifact) => {
  const htmlFile = artifact?.files.find((file) => file.language === 'html' || file.name.endsWith('.html'))
  return htmlFile?.content || null
}

const formatBytes = (chars: number) => {
  if (chars <= 0) return '0 B'
  const kb = chars / 1024
  return kb >= 1 ? `${kb.toFixed(1)} KB` : `${chars} B`
}

export default PreviewPanel
