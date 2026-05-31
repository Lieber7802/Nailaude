import { DiffOutlined, EyeOutlined } from '@ant-design/icons'
import type { Artifact } from '../../services/api'

interface DiffCardProps {
  artifact: Artifact
  onOpen?: () => void
}

const DiffCard = ({ artifact, onOpen }: DiffCardProps) => {
  const diff = artifact.diffData
  const lines = diff?.hunks.flatMap((hunk) => hunk.content.split('\n')) || []

  return (
    <article className="diff-card">
      <div className="diff-card__header">
        <span className="diff-card__icon">
          <DiffOutlined />
        </span>
        <span className="diff-card__title">
          <strong>{artifact.title}</strong>
          <small>
            +{diff?.additions || 0} / -{diff?.deletions || 0} · {diff?.file || 'diff'}
          </small>
        </span>
        <button aria-label="在右侧查看变更" type="button" onClick={onOpen}>
          <EyeOutlined />
          在右侧查看
        </button>
      </div>
      <pre className="diff-card__body">
        {lines.slice(0, 12).map((line, index) => (
          <span className={classForLine(line)} key={`${index}-${line}`}>
            {line || ' '}
          </span>
        ))}
      </pre>
    </article>
  )
}

const classForLine = (line: string) => {
  if (line.startsWith('+')) return 'diff-line diff-line--add'
  if (line.startsWith('-')) return 'diff-line diff-line--delete'
  if (line.startsWith('@@')) return 'diff-line diff-line--meta'
  return 'diff-line'
}

export default DiffCard
