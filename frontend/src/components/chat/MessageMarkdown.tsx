import type { ReactNode } from 'react'
import { parseInlineMarkdown, parseMarkdownBlocks, type MarkdownInlineNode } from '../../utils/markdownPreview'

interface MessageMarkdownProps {
  content: string
}

const MessageMarkdown = ({ content }: MessageMarkdownProps) => {
  const blocks = parseMarkdownBlocks(content)

  if (blocks.length === 0) return null

  return (
    <div className="message-markdown">
      {blocks.map((block, index) => {
        if (block.type === 'heading') return renderHeading(block.level, block.text, index)
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
            <div className="message-markdown__table-wrap" key={`${index}-${block.headers.join('-')}`}>
              <table>
                <thead>
                  <tr>
                    {block.headers.map((header, headerIndex) => (
                      <th key={`${headerIndex}-${header}`} style={{ textAlign: block.alignments[headerIndex] || 'left' }}>
                        {renderInlineMarkdown(header, index + headerIndex)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {block.rows.map((row, rowIndex) => (
                    <tr key={`${rowIndex}-${row.join('-')}`}>
                      {row.map((cell, cellIndex) => (
                        <td key={`${cellIndex}-${cell}`} style={{ textAlign: block.alignments[cellIndex] || 'left' }}>
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
        if (block.type === 'rule') return <hr key={`rule-${index}`} />
        return <p key={`${index}-${block.text}`}>{renderInlineMarkdown(block.text, index)}</p>
      })}
    </div>
  )
}

const renderInlineMarkdown = (text: string, keySeed: number): ReactNode[] => {
  return renderInlineNodes(parseInlineMarkdown(text), keySeed)
}

const renderInlineNodes = (nodes: MarkdownInlineNode[], keySeed: number): ReactNode[] => {
  return nodes.map((node, index) => {
    if (node.type === 'code') return <code key={`${keySeed}-code-${index}`}>{node.text}</code>
    if (node.type === 'strong') {
      return <strong key={`${keySeed}-strong-${index}`}>{renderInlineNodes(node.children, keySeed + index + 1)}</strong>
    }
    return node.text
  })
}

const renderHeading = (level: number, text: string, keySeed: number) => {
  const content = renderInlineMarkdown(text, keySeed)
  const key = `${keySeed}-${text}`

  if (level <= 1) return <h2 key={key}>{content}</h2>
  if (level === 2) return <h3 key={key}>{content}</h3>
  if (level === 3) return <h4 key={key}>{content}</h4>
  return <h5 key={key}>{content}</h5>
}

export default MessageMarkdown
