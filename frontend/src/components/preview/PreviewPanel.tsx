import { useArtifactStore } from '../../stores/artifactStore'

const PreviewPanel = () => {
  const artifactsByMessage = useArtifactStore((state) => state.artifactsByMessage)
  const activeArtifactId = useArtifactStore((state) => state.activeArtifactId)
  const artifacts = Object.values(artifactsByMessage).flat()
  const activeArtifact = artifacts.find((artifact) => artifact.id === activeArtifactId) || artifacts[0]
  const firstFile = activeArtifact?.files[0]

  return (
    <div className="preview-panel">
      <div className="preview-panel__header">
        <strong>Preview</strong>
      </div>
      <div className="preview-panel__body preview-panel__body--artifact">
        {activeArtifact ? (
          <>
            <strong>{activeArtifact.title}</strong>
            <small>{firstFile?.name}</small>
            <pre>{firstFile?.content.slice(0, 1200)}</pre>
          </>
        ) : (
          '等待产物生成'
        )}
      </div>
    </div>
  )
}

export default PreviewPanel
