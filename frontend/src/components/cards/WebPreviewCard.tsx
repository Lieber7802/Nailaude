import { CheckCircleFilled, ExportOutlined, EyeOutlined, GlobalOutlined } from '@ant-design/icons'
import type { Artifact } from '../../services/api'
import { getArtifactCardPresentation } from '../../utils/artifactCard'

interface WebPreviewCardProps {
  artifact: Artifact
  onOpen?: () => void
}

const WebPreviewCard = ({ artifact, onOpen }: WebPreviewCardProps) => {
  const presentation = getArtifactCardPresentation(artifact)
  const handleExternalOpen = () => {
    if (!artifact.previewUrl) return
    window.open(artifact.previewUrl, '_blank', 'noopener,noreferrer')
  }

  return (
    <article className="web-preview-card">
      <div className="web-preview-card__header">
        <span className="web-preview-card__icon">
          <GlobalOutlined />
        </span>
        <span className="web-preview-card__title">
          <strong>{presentation.title}</strong>
          <small>{presentation.detail}</small>
        </span>
        <span className="code-card__status">
          <CheckCircleFilled />
          {presentation.statusLabel}
        </span>
        <span className="web-preview-card__actions">
          <button aria-label="在右侧查看网页预览" type="button" onClick={onOpen}>
            <EyeOutlined />
            {presentation.actionLabel}
          </button>
          <button
            aria-label="新标签页打开预览"
            disabled={!artifact.previewUrl}
            title={artifact.previewUrl ? '新标签页打开预览' : '暂无预览链接'}
            type="button"
            onClick={handleExternalOpen}
          >
            <ExportOutlined />
          </button>
        </span>
      </div>
    </article>
  )
}

export default WebPreviewCard
