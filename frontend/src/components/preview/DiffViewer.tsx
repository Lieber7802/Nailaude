import { DiffEditor } from '@monaco-editor/react'
import { DiffOutlined } from '@ant-design/icons'
import type { Artifact } from '../../services/api'

interface DiffViewerProps {
  artifact?: Artifact
}

const DiffViewer = ({ artifact }: DiffViewerProps) => {
  const diff = artifact?.diffData
  if (!diff) {
    return (
      <div className="preview-empty">
        <DiffOutlined />
        当前没有可展示的变更对比
      </div>
    )
  }

  return (
    <div className="diff-viewer">
      <div className="diff-viewer__summary">
        <strong>{diff.file}</strong>
        <span>+{diff.additions}</span>
        <span>-{diff.deletions}</span>
      </div>
      <DiffEditor
        height="100%"
        language={languageFromFile(diff.file)}
        modified={diff.newContent || ''}
        original={diff.oldContent || ''}
        options={{ fontSize: 13, minimap: { enabled: false }, readOnly: true, renderSideBySide: true }}
        theme="vs"
      />
    </div>
  )
}

const languageFromFile = (file: string) => {
  const suffix = file.split('.').pop()?.toLowerCase()
  if (suffix === 'html') return 'html'
  if (suffix === 'css') return 'css'
  if (suffix === 'js') return 'javascript'
  if (suffix === 'ts') return 'typescript'
  if (suffix === 'tsx') return 'typescript'
  if (suffix === 'py') return 'python'
  return 'text'
}

export default DiffViewer
