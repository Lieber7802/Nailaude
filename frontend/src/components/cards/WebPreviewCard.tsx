import { EyeOutlined, GlobalOutlined } from '@ant-design/icons'
import type { Artifact } from '../../services/api'
import { getArtifactCardPresentation } from '../../utils/artifactCard'

interface WebPreviewCardProps {
  artifact: Artifact
  onOpen?: () => void
}

const WebPreviewCard = ({ artifact, onOpen }: WebPreviewCardProps) => {
  const presentation = getArtifactCardPresentation(artifact)

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
        <span className="web-preview-card__actions">
          <button aria-label="在右侧查看网页预览" type="button" onClick={onOpen}>
            <EyeOutlined />
            {presentation.actionLabel}
          </button>
        </span>
      </div>
    </article>
  )
}

export default WebPreviewCard
