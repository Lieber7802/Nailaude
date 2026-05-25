import { useState } from 'react'

interface MessageInputProps {
  disabled: boolean
  onSend: (content: string) => void
}

const MessageInput = ({ disabled, onSend }: MessageInputProps) => {
  const [content, setContent] = useState('')

  const handleSubmit = () => {
    const value = content.trim()
    if (!value) return
    onSend(value)
    setContent('')
  }

  return (
    <div className="message-input">
      <textarea
        disabled={disabled}
        onChange={(event) => setContent(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault()
            handleSubmit()
          }
        }}
        placeholder={disabled ? '请选择会话并等待连接' : '输入任务，按 Enter 发送'}
        value={content}
      />
      <button disabled={disabled || !content.trim()} type="button" onClick={handleSubmit}>
        发送
      </button>
    </div>
  )
}

export default MessageInput
