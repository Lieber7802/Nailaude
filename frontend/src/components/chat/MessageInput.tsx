import { DownOutlined, LinkOutlined, SendOutlined, StopOutlined } from '@ant-design/icons'
import { Button } from 'antd'
import { useMemo, useRef, useState } from 'react'
import type { Agent } from '../../services/api'
import { buildAttachmentSummary } from '../../utils/chatUi'
import MentionSelector from './MentionSelector'

interface SelectedAttachment {
  id: string
  name: string
  size: number
}

interface MessageInputProps {
  agents: Agent[]
  disabled: boolean
  canStop?: boolean
  onSend: (content: string) => void
  onStop?: () => void
}

const MessageInput = ({ agents, canStop = false, disabled, onSend, onStop }: MessageInputProps) => {
  const [content, setContent] = useState('')
  const [cursorIndex, setCursorIndex] = useState(0)
  const [mentionPickerOpen, setMentionPickerOpen] = useState(false)
  const [attachments, setAttachments] = useState<SelectedAttachment[]>([])
  const inputRef = useRef<HTMLTextAreaElement | null>(null)
  const fileInputRef = useRef<HTMLInputElement | null>(null)

  const mentionMatch = useMemo(() => {
    const textBeforeCursor = content.slice(0, cursorIndex)
    return /@([^\s@]*)$/.exec(textBeforeCursor)
  }, [content, cursorIndex])

  const handleSubmit = () => {
    const value = content.trim()
    const attachmentSummary = buildAttachmentSummary(attachments)
    const nextValue = [value, attachmentSummary ? `附件:\n${attachmentSummary}` : ''].filter(Boolean).join('\n\n')
    if (!nextValue) return
    onSend(nextValue)
    setContent('')
    setCursorIndex(0)
    setAttachments([])
  }

  const handleSelectMention = (agent: Agent) => {
    const start = mentionMatch ? cursorIndex - mentionMatch[0].length : cursorIndex
    const before = content.slice(0, start)
    const after = content.slice(cursorIndex)
    const needsLeadingSpace = before.length > 0 && !/\s$/.test(before)
    const insertion = `${needsLeadingSpace ? ' ' : ''}@${agent.name} `
    const nextContent = `${before}${insertion}${after}`
    const nextCursor = before.length + insertion.length
    setContent(nextContent)
    setCursorIndex(nextCursor)
    setMentionPickerOpen(false)
    window.setTimeout(() => {
      inputRef.current?.focus()
      inputRef.current?.setSelectionRange(nextCursor, nextCursor)
    }, 0)
  }

  const openMentionPicker = () => {
    if (disabled) return
    setMentionPickerOpen(true)
    inputRef.current?.focus()
  }

  const openAttachmentPicker = () => {
    if (disabled) return
    fileInputRef.current?.click()
  }

  const handleAttachmentChange = (files: FileList | null) => {
    if (!files) return
    const nextAttachments = Array.from(files).map((file) => ({
      id: `${file.name}-${file.size}-${file.lastModified}`,
      name: file.name,
      size: file.size,
    }))
    setAttachments((current) => {
      const currentIds = new Set(current.map((file) => file.id))
      return [...current, ...nextAttachments.filter((file) => !currentIds.has(file.id))]
    })
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const removeAttachment = (id: string) => {
    setAttachments((current) => current.filter((file) => file.id !== id))
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
            } else if (event.key === 'Escape') {
              setMentionPickerOpen(false)
            }
          }}
          onKeyUp={(event) => setCursorIndex(event.currentTarget.selectionStart)}
          placeholder={disabled ? '请选择会话并等待连接' : '输入任务，使用 @ 选择智能体，/ 选择快捷命令'}
          value={content}
        />
        <input
          ref={fileInputRef}
          multiple
          className="message-input__file"
          type="file"
          onChange={(event) => handleAttachmentChange(event.target.files)}
        />
        <MentionSelector
          agents={agents}
          query={mentionMatch?.[1] || ''}
          visible={!disabled && (mentionPickerOpen || Boolean(mentionMatch))}
          onSelect={handleSelectMention}
        />
        {attachments.length > 0 && (
          <div className="message-input__attachments" aria-label="已选择附件">
            {attachments.map((file) => (
              <span className="attachment-chip" key={file.id}>
                <LinkOutlined />
                {file.name}
                <button aria-label={`移除附件 ${file.name}`} type="button" onClick={() => removeAttachment(file.id)}>
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
        <div className="message-input__tools">
          <button type="button" onMouseDown={(event) => event.preventDefault()} onClick={openMentionPicker}>
            @ 智能体
          </button>
          <button type="button">/ 命令</button>
          <button type="button" onClick={openAttachmentPicker}>
            <LinkOutlined /> 附件
          </button>
        </div>
      </div>
      <div className="message-input__send">
        {canStop && (
          <Button
            aria-label="终止当前回复"
            className="message-input__stop"
            danger
            icon={<StopOutlined />}
            onClick={onStop}
          >
            终止
          </Button>
        )}
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
