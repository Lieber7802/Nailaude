import { DownOutlined, LinkOutlined, SendOutlined } from '@ant-design/icons'
import { Button } from 'antd'
import { useMemo, useRef, useState } from 'react'
import type { Agent } from '../../services/api'
import MentionSelector from './MentionSelector'

interface MessageInputProps {
  agents: Agent[]
  disabled: boolean
  onSend: (content: string) => void
}

const MessageInput = ({ agents, disabled, onSend }: MessageInputProps) => {
  const [content, setContent] = useState('')
  const [cursorIndex, setCursorIndex] = useState(0)
  const inputRef = useRef<HTMLTextAreaElement | null>(null)

  const mentionMatch = useMemo(() => {
    const textBeforeCursor = content.slice(0, cursorIndex)
    return /@([^\s@]*)$/.exec(textBeforeCursor)
  }, [content, cursorIndex])

  const handleSubmit = () => {
    const value = content.trim()
    if (!value) return
    onSend(value)
    setContent('')
    setCursorIndex(0)
  }

  const handleSelectMention = (agent: Agent) => {
    if (!mentionMatch) return
    const start = cursorIndex - mentionMatch[0].length
    const before = content.slice(0, start)
    const after = content.slice(cursorIndex)
    const insertion = `@${agent.name} `
    const nextContent = `${before}${insertion}${after}`
    const nextCursor = before.length + insertion.length
    setContent(nextContent)
    setCursorIndex(nextCursor)
    window.setTimeout(() => {
      inputRef.current?.focus()
      inputRef.current?.setSelectionRange(nextCursor, nextCursor)
    }, 0)
  }

  return (
    <div className="message-input">
      <div className="message-input__editor">
        <textarea
          ref={inputRef}
          disabled={disabled}
          onChange={(event) => {
            setContent(event.target.value)
            setCursorIndex(event.target.selectionStart)
          }}
          onClick={(event) => setCursorIndex(event.currentTarget.selectionStart)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
              event.preventDefault()
              handleSubmit()
            }
          }}
          onKeyUp={(event) => setCursorIndex(event.currentTarget.selectionStart)}
          placeholder={disabled ? '请选择会话并等待连接' : '输入任务，使用 @ 选择 Agent，/ 选择快捷命令'}
          value={content}
        />
        <MentionSelector
          agents={agents}
          query={mentionMatch?.[1] || ''}
          visible={!disabled && Boolean(mentionMatch)}
          onSelect={handleSelectMention}
        />
        <div className="message-input__tools">
          <button type="button">@ 代理</button>
          <button type="button">/ 命令</button>
          <button type="button">
            <LinkOutlined /> 附件
          </button>
        </div>
      </div>
      <div className="message-input__send">
        <Button
          disabled={disabled || !content.trim()}
          icon={<SendOutlined />}
          type="primary"
          onClick={handleSubmit}
        />
        <button aria-label="更多发送选项" type="button">
          <DownOutlined />
        </button>
      </div>
    </div>
  )
}

export default MessageInput
