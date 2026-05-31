import { ExportOutlined, EyeOutlined, GlobalOutlined } from '@ant-design/icons'
import type { Artifact } from '../../services/api'

interface WebPreviewCardProps {
  artifact: Artifact
  onOpen?: () => void
}

const WebPreviewCard = ({ artifact, onOpen }: WebPreviewCardProps) => {
  const html = artifact.files.find((file) => file.language === 'html' || file.name.endsWith('.html'))?.content
  const handleExternalOpen = () => {
    if (!artifact.previewUrl) return
    window.open(artifact.previewUrl, '_blank', 'noopener,noreferrer')
  }

  return (
    <article className="web-preview-card">
      <div className="web-preview-card__header">
        <span>
          <GlobalOutlined />
          <strong>{artifact.title}</strong>
        </span>
        <span className="web-preview-card__actions">
          <button aria-label="在右侧查看网页预览" type="button" onClick={onOpen}>
            <EyeOutlined />
            在右侧查看
          </button>
          <button
            aria-label="新标签页打开预览"
            disabled={!artifact.previewUrl}
            title={artifact.previewUrl ? '新标签页打开预览' : '暂无预览链接'}
            type="button"
            onClick={handleExternalOpen}
          >
            <ExportOutlined />
          </button>
        </span>
      </div>
      <button className="web-preview-card__frame" type="button" onClick={onOpen}>
        {html ? <iframe sandbox="" srcDoc={html} title={artifact.title} /> : <span>预览文件待加载</span>}
      </button>
    </article>
  )
}

export default WebPreviewCard
