import { CodeOutlined, ExpandOutlined, FileTextOutlined, GlobalOutlined } from '@ant-design/icons'
import { useEffect, useMemo, useState } from 'react'
import type { Artifact } from '../../services/api'
import { useArtifactStore } from '../../stores/artifactStore'
import CodeEditor from './CodeEditor'
import DiffViewer from './DiffViewer'
import IframePreview from './IframePreview'

type PreviewTab = 'outputs' | 'preview' | 'code' | 'changes'
type PreviewViewport = 'desktop' | 'tablet' | 'mobile'

const MIN_ZOOM = 75
const MAX_ZOOM = 125

const PreviewPanel = () => {
  const [activeTab, setActiveTab] = useState<PreviewTab>('preview')
  const [viewport, setViewport] = useState<PreviewViewport>('desktop')
  const [zoom, setZoom] = useState(100)
  const [fullscreen, setFullscreen] = useState(false)
  const artifactsByMessage = useArtifactStore((state) => state.artifactsByMessage)
  const storedActiveArtifact = useArtifactStore((state) => state.activeArtifact)
  const activeArtifactId = useArtifactStore((state) => state.activeArtifactId)
  const openRevision = useArtifactStore((state) => state.openRevision)
  const setActiveArtifact = useArtifactStore((state) => state.setActiveArtifact)
  const artifacts = useMemo(() => {
    const allArtifacts = Object.values(artifactsByMessage).flat()
    if (storedActiveArtifact && !allArtifacts.some((artifact) => artifact.id === storedActiveArtifact.id)) {
      return [storedActiveArtifact, ...allArtifacts]
    }
    return allArtifacts
  }, [artifactsByMessage, storedActiveArtifact])
  const activeArtifact =
    storedActiveArtifact || artifacts.find((artifact) => artifact.id === activeArtifactId) || artifacts[0]
  const firstFile = activeArtifact?.files[0]

  useEffect(() => {
    if (activeArtifact?.type === 'diff') setActiveTab('changes')
    else if (activeArtifact?.type === 'code') setActiveTab('code')
    else if (activeArtifact?.type === 'webpage') setActiveTab('preview')
  }, [activeArtifact?.id, activeArtifact?.type, openRevision])

  return (
    <div className={fullscreen ? 'preview-panel preview-panel--fullscreen' : 'preview-panel'}>
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
          <button className={activeTab === 'code' ? 'is-active' : ''} type="button" onClick={() => setActiveTab('code')}>
            代码
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
          <button aria-label="展开预览" type="button" onClick={() => setFullscreen(!fullscreen)}>
            <ExpandOutlined />
          </button>
        </div>
      </div>

      <div className="preview-panel__body">
        {activeTab === 'outputs' && (
          <OutputsTab artifacts={artifacts} activeArtifact={activeArtifact} onSelect={setActiveArtifact} />
        )}
        {activeTab === 'preview' && (
          <IframePreview
            artifact={activeArtifact}
            viewport={viewport}
            zoom={zoom}
            onViewportChange={setViewport}
            onZoomChange={(nextZoom) => setZoom(Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, nextZoom)))}
          />
        )}
        {activeTab === 'code' && <CodeEditor file={firstFile} />}
        {activeTab === 'changes' && <DiffViewer artifact={activeArtifact} />}
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
    return <div className="preview-empty">点击聊天中的产物卡片，在此预览</div>
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
            <span className="output-row__icon">{iconForArtifact(artifact)}</span>
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

const iconForArtifact = (artifact: Artifact) => {
  if (artifact.type === 'webpage') return <GlobalOutlined />
  return <CodeOutlined />
}

const formatBytes = (chars: number) => {
  if (chars <= 0) return '0 B'
  const kb = chars / 1024
  return kb >= 1 ? `${kb.toFixed(1)} KB` : `${chars} B`
}

export default PreviewPanel
