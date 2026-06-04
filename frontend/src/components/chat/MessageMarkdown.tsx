import DOMPurify from 'dompurify'
import { renderMarkdownToHtml } from '../../utils/markdownPreview'

interface MessageMarkdownProps {
  content: string
}

const MessageMarkdown = ({ content }: MessageMarkdownProps) => {
  const html = DOMPurify.sanitize(renderMarkdownToHtml(content))

  if (!html) return null
  return <div className="message-markdown" dangerouslySetInnerHTML={{ __html: html }} />
}

export default MessageMarkdown
