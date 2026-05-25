import MessageBubble from './MessageBubble'
import MessageInput from './MessageInput'
import type { Conversation, Message } from '../../services/api'

interface ChatAreaProps {
  conversation: Conversation | null
  messages: Message[]
  wsStatus: string
  onSend: (content: string) => void
}

const ChatArea = ({ conversation, messages, onSend, wsStatus }: ChatAreaProps) => {
  const disabled = !conversation || wsStatus !== 'open'

  return (
    <div className="chat-area">
      <header className="chat-area__header">
        <div>
          <strong>{conversation?.title || '选择或创建会话'}</strong>
          <small>{conversation?.workDir || '工作目录未设置'}</small>
        </div>
        <span className={`status-dot status-dot--${wsStatus}`}>{wsStatus}</span>
      </header>
      <div className="chat-area__body chat-area__body--messages">
        {messages.length === 0 ? (
          <div className="empty-state">发送第一条消息，Mock Agent 会返回流式产物</div>
        ) : (
          messages.map((message) => <MessageBubble key={message.id} message={message} />)
        )}
      </div>
      <MessageInput disabled={disabled} onSend={onSend} />
    </div>
  )
}

export default ChatArea
