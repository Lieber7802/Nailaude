import { CheckCircleFilled, CodeOutlined, EyeOutlined, FileTextOutlined } from '@ant-design/icons'
import type { Artifact } from '../../services/api'

interface CodeCardProps {
  artifact: Artifact
  onOpen?: (artifactId: string) => void
}

const CodeCard = ({ artifact, onOpen }: CodeCardProps) => {
  const firstFile = artifact.files[0]
  const language = firstFile?.language || 'text'

  return (
    <article className="code-card">
      <div className="code-card__icon">{language === 'markdown' || language === 'md' ? <FileTextOutlined /> : <CodeOutlined />}</div>
      <div className="code-card__main">
        <strong>{artifact.title}</strong>
        <small>
          {language.toUpperCase()} · {formatBytes(firstFile?.content.length || 0)}
        </small>
      </div>
      <span className="code-card__status">
        <CheckCircleFilled />
        已生成
      </span>
      <button type="button" onClick={() => onOpen?.(artifact.id)}>
        <EyeOutlined />
        预览
      </button>
    </article>
  )
}

const formatBytes = (chars: number) => {
  if (chars <= 0) return '0 B'
  const kb = chars / 1024
  return kb >= 1 ? `${kb.toFixed(1)} KB` : `${chars} B`
}

export default CodeCard
