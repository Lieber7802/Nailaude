import { DiffOutlined, EyeOutlined } from '@ant-design/icons'
import type { Artifact } from '../../services/api'
import { getArtifactCardPresentation } from '../../utils/artifactCard'

interface DiffCardProps {
  artifact: Artifact
  onOpen?: () => void
}

const DiffCard = ({ artifact, onOpen }: DiffCardProps) => {
  const presentation = getArtifactCardPresentation(artifact)

  return (
    <article className="diff-card">
      <div className="diff-card__header">
        <span className="diff-card__icon">
          <DiffOutlined />
        </span>
        <span className="diff-card__title">
          <strong>{presentation.title}</strong>
          <small>{presentation.detail}</small>
        </span>
        <button aria-label="在右侧查看变更" type="button" onClick={onOpen}>
          <EyeOutlined />
          {presentation.actionLabel}
        </button>
      </div>
    </article>
  )
}

export default DiffCard
