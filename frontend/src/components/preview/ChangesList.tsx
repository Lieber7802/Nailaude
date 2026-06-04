import { DiffEditor } from '@monaco-editor/react'
import { DownOutlined, FileTextOutlined, RightOutlined } from '@ant-design/icons'
import { useState } from 'react'
import type { Artifact } from '../../services/api'

interface ChangesListProps {
  artifacts: Artifact[]
}

const ChangesList = ({ artifacts }: ChangesListProps) => {
  const [expandedIds, setExpandedIds] = useState<Record<string, boolean>>({})

  if (artifacts.length === 0) {
    return (
      <div className="preview-empty">
        <FileTextOutlined />
        当前没有可展示的文件变更
      </div>
    )
  }

  return (
    <div className="changes-list">
      {artifacts.map((artifact) => {
        const diff = artifact.diffData
        if (!diff) return null

        const expanded = Boolean(expandedIds[artifact.id])
        return (
          <article className={expanded ? 'change-row is-expanded' : 'change-row'} key={artifact.id}>
            <button
              aria-expanded={expanded}
              className="change-row__header"
              type="button"
              onClick={() => setExpandedIds((state) => ({ ...state, [artifact.id]: !expanded }))}
            >
              <span className="change-row__chevron">{expanded ? <DownOutlined /> : <RightOutlined />}</span>
              <span className="change-row__file">
                <strong>{diff.file}</strong>
                <small>{artifact.title}</small>
              </span>
              <span className="change-row__stats">
                <span>+{diff.additions}</span>
                <span>-{diff.deletions}</span>
              </span>
            </button>
            {expanded && (
              <div className="change-row__details">
                <DiffEditor
                  height="420px"
                  language={languageFromFile(diff.file)}
                  modified={diff.newContent || ''}
                  original={diff.oldContent || ''}
                  options={{
                    fontSize: 13,
                    minimap: { enabled: false },
                    readOnly: true,
                    renderSideBySide: true,
                    scrollBeyondLastLine: false,
                  }}
                  theme="vs"
                />
              </div>
            )}
          </article>
        )
      })}
    </div>
  )
}

const languageFromFile = (file: string) => {
  const suffix = file.split('.').pop()?.toLowerCase()
  if (suffix === 'html') return 'html'
  if (suffix === 'css') return 'css'
  if (suffix === 'js') return 'javascript'
  if (suffix === 'jsx') return 'javascript'
  if (suffix === 'ts') return 'typescript'
  if (suffix === 'tsx') return 'typescript'
  if (suffix === 'py') return 'python'
  if (suffix === 'md') return 'markdown'
  return 'text'
}

export default ChangesList
