import type { Agent, Conversation } from '../../services/api'

interface ConversationListProps {
  agents: Agent[]
  conversations: Conversation[]
  activeId: string | null
  onSelect: (id: string) => void
  onCreate: () => void
}

const ConversationList = ({ agents, conversations, activeId, onCreate, onSelect }: ConversationListProps) => {
  return (
    <div className="sidebar">
      <div className="sidebar__header">
        <strong>AgentHub</strong>
        <button type="button" onClick={onCreate} aria-label="新建会话">
          +
        </button>
      </div>
      <section className="sidebar__section">
        <span className="sidebar__label">Agents</span>
        <div className="agent-list">
          {agents.map((agent) => (
            <div className="agent-row" key={agent.id}>
              <span>{agent.avatar}</span>
              <div>
                <strong>{agent.name}</strong>
                <small>{agent.capabilities.slice(0, 2).join(' / ')}</small>
              </div>
            </div>
          ))}
        </div>
      </section>
      <section className="sidebar__section">
        <span className="sidebar__label">Conversations</span>
        <div className="conversation-list">
          {conversations.map((conversation) => (
            <button
              className={conversation.id === activeId ? 'conversation-row is-active' : 'conversation-row'}
              key={conversation.id}
              type="button"
              onClick={() => onSelect(conversation.id)}
            >
              <strong>{conversation.title}</strong>
              <small>{conversation.type} · {conversation.workDir || '未指定目录'}</small>
            </button>
          ))}
        </div>
      </section>
    </div>
  )
}

export default ConversationList
