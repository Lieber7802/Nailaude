import {
  CodeOutlined,
  CompressOutlined,
  ExpandOutlined,
  FileTextOutlined,
  GlobalOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons'
import { useEffect, useMemo, useRef, useState } from 'react'
import type { Artifact } from '../../services/api'
import { useArtifactStore } from '../../stores/artifactStore'
import { useUIStore } from '../../stores/uiStore'
import CodeEditor from './CodeEditor'
import DiffViewer from './DiffViewer'
import IframePreview from './IframePreview'
import MarkdownPreview from './MarkdownPreview'
import { findMarkdownFile, getArtifactPreviewMode, isMarkdownFile } from '../../utils/markdownPreview'
import { FULLSCREEN_ACTIONS, type PreviewViewport } from '../../utils/previewControls'

type PreviewTab = 'outputs' | 'preview' | 'code' | 'changes'

const MIN_ZOOM = 75
const MAX_ZOOM = 125

const PreviewPanel = () => {
  const panelRef = useRef<HTMLDivElement>(null)
  const [tabSelection, setTabSelection] = useState<{
    artifactId: string | null
    openRevision: number
    tab: PreviewTab
  }>({ artifactId: null, openRevision: -1, tab: 'preview' })
  const [viewport, setViewport] = useState<PreviewViewport>('desktop')
  const [zoom, setZoom] = useState(100)
  const [fullscreen, setFullscreen] = useState(false)
  const [fullscreenFallback, setFullscreenFallback] = useState(false)
  const artifactsByMessage = useArtifactStore((state) => state.artifactsByMessage)
  const storedActiveArtifact = useArtifactStore((state) => state.activeArtifact)
  const activeArtifactId = useArtifactStore((state) => state.activeArtifactId)
  const openRevision = useArtifactStore((state) => state.openRevision)
  const setActiveArtifact = useArtifactStore((state) => state.setActiveArtifact)
  const setPreviewVisible = useUIStore((state) => state.setPreviewVisible)
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
  const markdownFile = findMarkdownFile(activeArtifact)
  const previewMode = getArtifactPreviewMode(activeArtifact)
  const activeTab =
    tabSelection.artifactId === (activeArtifact?.id || null) && tabSelection.openRevision === openRevision
      ? tabSelection.tab
      : tabForArtifact(activeArtifact)
  const setActiveTab = (tab: PreviewTab) =>
    setTabSelection({ artifactId: activeArtifact?.id || null, openRevision, tab })
  const isFullscreen = fullscreen || fullscreenFallback
  const fullscreenAction = isFullscreen ? FULLSCREEN_ACTIONS.exit : FULLSCREEN_ACTIONS.enter

  useEffect(() => {
    const syncFullscreenState = () => {
      const isPanelFullscreen = document.fullscreenElement === panelRef.current
      setFullscreen(isPanelFullscreen)
      if (document.fullscreenElement && !isPanelFullscreen) {
        setFullscreenFallback(false)
      }
    }

    document.addEventListener('fullscreenchange', syncFullscreenState)
    return () => document.removeEventListener('fullscreenchange', syncFullscreenState)
  }, [])

  const toggleFullscreen = async () => {
    if (isFullscreen) {
      setFullscreenFallback(false)
      if (document.fullscreenElement) {
        await document.exitFullscreen()
      } else {
        setFullscreen(false)
      }
      return
    }

    const panel = panelRef.current
    if (!panel?.requestFullscreen) {
      setFullscreenFallback(true)
      setFullscreen(true)
      return
    }

    try {
      await panel.requestFullscreen()
    } catch {
      setFullscreenFallback(true)
      setFullscreen(true)
    }
  }

  return (
    <div className={isFullscreen ? 'preview-panel preview-panel--fullscreen' : 'preview-panel'} ref={panelRef}>
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
          <button className="preview-toolbar__file" title={firstFile?.name || '暂无文件'} type="button">
            <FileTextOutlined />
            <span className="preview-toolbar__file-name">{firstFile?.name || '暂无文件'}</span>
          </button>
          <button
            aria-label={fullscreenAction.ariaLabel}
            title={fullscreenAction.label}
            type="button"
            onClick={() => void toggleFullscreen()}
          >
            {isFullscreen ? <CompressOutlined /> : <ExpandOutlined />}
          </button>
          <button
            aria-label="隐藏预览窗格"
            className="pane-toggle pane-toggle--preview"
            title="隐藏预览窗格"
            type="button"
            onClick={() => setPreviewVisible(false)}
          >
            <MenuUnfoldOutlined />
          </button>
        </div>
      </div>

      <div className="preview-panel__body">
        {activeTab === 'outputs' && (
          <OutputsTab artifacts={artifacts} activeArtifact={activeArtifact} onSelect={setActiveArtifact} />
        )}
        {activeTab === 'preview' && previewMode === 'markdown' && <MarkdownPreview file={markdownFile} />}
        {activeTab === 'preview' && previewMode !== 'markdown' && (
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
  if (isMarkdownFile(artifact.files[0])) return <FileTextOutlined />
  return <CodeOutlined />
}

const tabForArtifact = (artifact?: Artifact): PreviewTab => {
  if (artifact?.type === 'diff') return 'changes'
  if (getArtifactPreviewMode(artifact) === 'markdown') return 'preview'
  if (artifact?.type === 'code') return 'code'
  return 'preview'
}

const formatBytes = (chars: number) => {
  if (chars <= 0) return '0 B'
  const kb = chars / 1024
  return kb >= 1 ? `${kb.toFixed(1)} KB` : `${chars} B`
}

export default PreviewPanel
