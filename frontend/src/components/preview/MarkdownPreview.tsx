import type { ReactNode } from 'react'
import type { ArtifactFile } from '../../services/api'
import { parseMarkdownBlocks } from '../../utils/markdownPreview'

interface MarkdownPreviewProps {
  compact?: boolean
  file?: ArtifactFile
}

const MarkdownPreview = ({ compact = false, file }: MarkdownPreviewProps) => {
  if (!file) {
    return <div className="preview-empty">当前产出物没有可预览的 Markdown 文件</div>
  }

  const blocks = parseMarkdownBlocks(file.content)

  return (
    <article className={compact ? 'markdown-preview markdown-preview--compact' : 'markdown-preview'}>
      {!compact && (
        <div className="markdown-preview__header">
          <strong>{file.name}</strong>
          <small>MARKDOWN</small>
        </div>
      )}
      <div className="markdown-preview__body">
        {blocks.map((block, index) => {
          if (block.type === 'heading') {
            return renderHeading(block.level, block.text, index)
          }
          if (block.type === 'list') {
            const ListTag = block.ordered ? 'ol' : 'ul'
            return (
              <ListTag key={`${index}-${block.items.join('-')}`}>
                {block.items.map((item, itemIndex) => (
                  <li key={`${itemIndex}-${item}`}>{renderInlineMarkdown(item, index + itemIndex)}</li>
                ))}
              </ListTag>
            )
          }
          if (block.type === 'table') {
            return (
              <div className="markdown-preview__table-wrap" key={`${index}-${block.headers.join('-')}`}>
                <table>
                  <thead>
                    <tr>
                      {block.headers.map((header, headerIndex) => (
                        <th
                          key={`${headerIndex}-${header}`}
                          style={{ textAlign: block.alignments[headerIndex] || 'left' }}
                        >
                          {renderInlineMarkdown(header, index + headerIndex)}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {block.rows.map((row, rowIndex) => (
                      <tr key={`${rowIndex}-${row.join('-')}`}>
                        {row.map((cell, cellIndex) => (
                          <td
                            key={`${cellIndex}-${cell}`}
                            style={{ textAlign: block.alignments[cellIndex] || 'left' }}
                          >
                            {renderInlineMarkdown(cell, index + rowIndex + cellIndex)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )
          }
          if (block.type === 'code') {
            return (
              <pre key={`${index}-${block.language}`} data-language={block.language.toUpperCase()}>
                <code>{block.code || ' '}</code>
              </pre>
            )
          }
          if (block.type === 'rule') {
            return <hr key={`rule-${index}`} />
          }
          return <p key={`${index}-${block.text}`}>{renderInlineMarkdown(block.text, index)}</p>
        })}
      </div>
    </article>
  )
}

const renderInlineMarkdown = (text: string, keySeed: number): ReactNode[] => {
  const nodes: ReactNode[] = []
  const tokenPattern = /(`[^`]+`|\*\*[^*]+?\*\*)/g
  let cursor = 0
  let match = tokenPattern.exec(text)

  while (match) {
    if (match.index > cursor) {
      nodes.push(text.slice(cursor, match.index))
    }

    const token = match[0]
    if (token.startsWith('`')) {
      nodes.push(<code key={`${keySeed}-code-${match.index}`}>{token.slice(1, -1)}</code>)
    } else {
      nodes.push(<strong key={`${keySeed}-strong-${match.index}`}>{token.slice(2, -2)}</strong>)
    }

    cursor = match.index + token.length
    match = tokenPattern.exec(text)
  }

  if (cursor < text.length) {
    nodes.push(text.slice(cursor))
  }

  return nodes.length > 0 ? nodes : [text]
}

const renderHeading = (level: number, text: string, keySeed: number) => {
  const content = renderInlineMarkdown(text, keySeed)
  const key = `${keySeed}-${text}`

  if (level <= 1) return <h2 key={key}>{content}</h2>
  if (level === 2) return <h3 key={key}>{content}</h3>
  if (level === 3) return <h4 key={key}>{content}</h4>
  if (level === 4) return <h5 key={key}>{content}</h5>
  return <h6 key={key}>{content}</h6>
}

export default MarkdownPreview
