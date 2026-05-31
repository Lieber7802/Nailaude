import Editor from '@monaco-editor/react'
import type { ArtifactFile } from '../../services/api'

interface CodeEditorProps {
  file?: ArtifactFile
}

const CodeEditor = ({ file }: CodeEditorProps) => {
  if (!file) {
    return <div className="preview-empty">当前产出物没有可查看的代码文件</div>
  }

  return (
    <div className="code-editor">
      <div className="code-editor__header">
        <strong>{file.name}</strong>
        <small>{file.language.toUpperCase()}</small>
      </div>
      <Editor
        height="100%"
        language={file.language}
        options={{ fontSize: 13, minimap: { enabled: false }, readOnly: true, wordWrap: 'on' }}
        theme="vs"
        value={file.content}
      />
    </div>
  )
}

export default CodeEditor
