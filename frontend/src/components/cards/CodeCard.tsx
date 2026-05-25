import type { Artifact } from '../../services/api'

interface CodeCardProps {
  artifact: Artifact
  onOpen?: (artifactId: string) => void
}

const CodeCard = ({ artifact, onOpen }: CodeCardProps) => {
  const firstFile = artifact.files[0]

  return (
    <article className="code-card">
      <header className="code-card__header">
        <div>
          <strong>{artifact.title}</strong>
          <small>{firstFile?.language || 'text'}</small>
        </div>
        <button type="button" onClick={() => onOpen?.(artifact.id)}>
          查看
        </button>
      </header>
      <pre className="code-card__body">
        <code>{firstFile?.content || ''}</code>
      </pre>
    </article>
  )
}

export default CodeCard
