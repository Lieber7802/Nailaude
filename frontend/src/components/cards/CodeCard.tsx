import { CheckCircleFilled, CodeOutlined, CopyOutlined, EyeOutlined, FileTextOutlined } from '@ant-design/icons'
import { useState } from 'react'
import type { Artifact } from '../../services/api'
import { getArtifactCardPresentation } from '../../utils/artifactCard'

interface CodeCardProps {
  artifact: Artifact
  onOpen?: () => void
}

const CodeCard = ({ artifact, onOpen }: CodeCardProps) => {
  const [copied, setCopied] = useState(false)
  const firstFile = artifact.files[0]
  const presentation = getArtifactCardPresentation(artifact)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(firstFile?.content || '')
    setCopied(true)
    window.setTimeout(() => setCopied(false), 1200)
  }

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
        <span className="code-card__status">
          <CheckCircleFilled />
          {presentation.statusLabel}
        </span>
        <div className="code-card__actions">
          <button aria-label="复制代码" type="button" onClick={() => void handleCopy()}>
            <CopyOutlined />
            {copied ? '已复制' : '复制'}
          </button>
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
