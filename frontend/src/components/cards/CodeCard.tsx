import {
  CheckCircleFilled,
  CodeOutlined,
  CopyOutlined,
  DownOutlined,
  EyeOutlined,
  FileTextOutlined,
  UpOutlined,
} from '@ant-design/icons'
import { useMemo, useState } from 'react'
import type { Artifact } from '../../services/api'

interface CodeCardProps {
  artifact: Artifact
  onOpen?: () => void
}

const CodeCard = ({ artifact, onOpen }: CodeCardProps) => {
  const [copied, setCopied] = useState(false)
  const [expanded, setExpanded] = useState(false)
  const firstFile = artifact.files[0]
  const language = firstFile?.language || 'text'
  const lines = useMemo(() => (firstFile?.content || '').split('\n'), [firstFile?.content])
  const visibleLines = expanded ? lines : lines.slice(0, 8)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(firstFile?.content || '')
    setCopied(true)
    window.setTimeout(() => setCopied(false), 1200)
  }

  return (
    <article className="code-card">
      <div className="code-card__summary">
        <div className="code-card__icon">
          {language === 'markdown' || language === 'md' ? <FileTextOutlined /> : <CodeOutlined />}
        </div>
        <div className="code-card__main">
          <strong>{artifact.title}</strong>
          <small>
            {language.toUpperCase()} · {lines.length} 行 · {formatBytes(firstFile?.content.length || 0)}
          </small>
        </div>
        <span className="code-card__status">
          <CheckCircleFilled />
          已生成
        </span>
        <div className="code-card__actions">
          <button aria-label="复制代码" type="button" onClick={() => void handleCopy()}>
            <CopyOutlined />
            {copied ? '已复制' : '复制'}
          </button>
          <button aria-label="在右侧查看代码" type="button" onClick={onOpen}>
            <EyeOutlined />
            在右侧查看
          </button>
          <button aria-label={expanded ? '折叠代码' : '展开代码'} type="button" onClick={() => setExpanded(!expanded)}>
            {expanded ? <UpOutlined /> : <DownOutlined />}
          </button>
        </div>
      </div>
      <div className="code-card__preview">
        {visibleLines.map((line, index) => (
          <div className="code-line" key={`${index}-${line}`}>
            <span className="code-line__number">{index + 1}</span>
            <code>{line || ' '}</code>
          </div>
        ))}
        {!expanded && lines.length > visibleLines.length && (
          <button className="code-card__more" type="button" onClick={() => setExpanded(true)}>
            展开 {lines.length - visibleLines.length} 行
          </button>
        )}
      </div>
    </article>
  )
}

const formatBytes = (chars: number) => {
  if (chars <= 0) return '0 B'
  const kb = chars / 1024
  return kb >= 1 ? `${kb.toFixed(1)} KB` : `${chars} B`
}

export default CodeCard
