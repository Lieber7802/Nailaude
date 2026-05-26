import { DeleteOutlined, PlusOutlined, SearchOutlined } from '@ant-design/icons'
import { Button, Empty, Input, Popconfirm, Tag } from 'antd'
import type { Agent, Conversation } from '../../services/api'

interface ConversationListProps {
  agents: Agent[]
  conversations: Conversation[]
  activeId: string | null
  search: string
  onSearch: (value: string) => void
  onSelect: (id: string) => void
  onCreate: () => void
  onDelete: (id: string) => void
}

const ConversationList = ({
  agents,
  conversations,
  activeId,
  onCreate,
  onDelete,
  onSearch,
  onSelect,
  search,
}: ConversationListProps) => {
  const agentsById = new Map(agents.map((agent) => [agent.id, agent]))

  return (
    <div className="sidebar">
      <div className="sidebar__header">
        <strong>AgentHub</strong>
        <Button aria-label="新建会话" icon={<PlusOutlined />} size="small" type="primary" onClick={onCreate} />
      </div>
      <section className="sidebar__section">
        <span className="sidebar__label">Agents</span>
        <div className="agent-list">
          {agents.map((agent) => (
            <div className="agent-row" key={agent.id}>
              <span className="agent-row__avatar">{agent.avatar}</span>
              <div>
                <strong>{agent.name}</strong>
                <small>{agent.capabilities.slice(0, 2).join(' / ')}</small>
              </div>
            </div>
          ))}
        </div>
      </section>
      <section className="sidebar__section sidebar__section--fill">
        <div className="sidebar__section-title">
          <span className="sidebar__label">Conversations</span>
        </div>
        <Input
          allowClear
          className="conversation-search"
          placeholder="搜索会话或最近消息"
          prefix={<SearchOutlined />}
          value={search}
          onChange={(event) => onSearch(event.target.value)}
        />
        <div className="conversation-list">
          {conversations.length === 0 ? (
            <Empty description="暂无会话" image={Empty.PRESENTED_IMAGE_SIMPLE} />
          ) : (
            conversations.map((conversation) => {
              const participants = conversation.participantIds
                .map((id) => agentsById.get(id))
                .filter((agent): agent is Agent => Boolean(agent))
              return (
                <div
                  className={conversation.id === activeId ? 'conversation-row is-active' : 'conversation-row'}
                  key={conversation.id}
                >
                  <button className="conversation-row__main" type="button" onClick={() => onSelect(conversation.id)}>
                    <span className="conversation-row__title">{conversation.title}</span>
                    <span className="conversation-row__meta">
                      <Tag color={conversation.type === 'group' ? 'blue' : 'green'}>
                        {conversation.type === 'group' ? '群聊' : '单聊'}
                      </Tag>
                      {participants.map((agent) => agent.name).join('、') || '未选择 Agent'}
                    </span>
                    <span className="conversation-row__last">{conversation.lastMessage || '还没有消息'}</span>
                  </button>
                  <Popconfirm title="删除这个会话？" okText="删除" cancelText="取消" onConfirm={() => onDelete(conversation.id)}>
                    <Button aria-label="删除会话" icon={<DeleteOutlined />} size="small" type="text" />
                  </Popconfirm>
                </div>
              )
            })
          )}
        </div>
      </section>
    </div>
  )
}

export default ConversationList
