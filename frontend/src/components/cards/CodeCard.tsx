import { CodeOutlined, EyeOutlined, FileTextOutlined } from '@ant-design/icons'
import type { Artifact } from '../../services/api'
import { getArtifactCardPresentation } from '../../utils/artifactCard'

interface CodeCardProps {
  artifact: Artifact
  onOpen?: () => void
}

const CodeCard = ({ artifact, onOpen }: CodeCardProps) => {
  const presentation = getArtifactCardPresentation(artifact)

  return (
    <article className="code-card">
      <div className="code-card__summary">
        <div className="code-card__icon">
          {presentation.kind === 'markdown' || presentation.kind === 'file' ? <FileTextOutlined /> : <CodeOutlined />}
        </div>
        <div className="code-card__main">
          <strong>{presentation.title}</strong>
          <small>{presentation.detail}</small>
        </div>
        <div className="code-card__actions">
          <button aria-label={presentation.actionLabel} type="button" onClick={onOpen}>
            <EyeOutlined />
            {presentation.actionLabel}
          </button>
        </div>
      </div>
    </article>
  )
}

export default CodeCard
