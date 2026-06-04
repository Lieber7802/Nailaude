import DOMPurify from 'dompurify'
import type { ArtifactFile } from '../../services/api'
import { renderMarkdownToHtml } from '../../utils/markdownPreview'

interface MarkdownPreviewProps {
  compact?: boolean
  file?: ArtifactFile
}

const MarkdownPreview = ({ compact = false, file }: MarkdownPreviewProps) => {
  if (!file) {
    return <div className="preview-empty">当前产出物没有可预览的 Markdown 文件</div>
  }

  const html = DOMPurify.sanitize(renderMarkdownToHtml(file.content))

  return (
    <article className={compact ? 'markdown-preview markdown-preview--compact' : 'markdown-preview'}>
      {!compact && (
        <div className="markdown-preview__header">
          <strong>{file.name}</strong>
          <small>MARKDOWN</small>
        </div>
      )}
      <div className="markdown-preview__body" dangerouslySetInnerHTML={{ __html: html }} />
    </article>
  )
}

export default MarkdownPreview
