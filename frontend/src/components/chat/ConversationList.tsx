import {
  ArrowRightOutlined,
  DeleteOutlined,
  HomeFilled,
  PlusOutlined,
  SearchOutlined,
  SettingOutlined,
} from '@ant-design/icons'
import { Button, Empty, Input, Popconfirm } from 'antd'
import type { Agent, Conversation } from '../../services/api'

interface ConversationListProps {
  agents: Agent[]
  conversations: Conversation[]
  activeId: string | null
  search: string
  onSearch: (value: string) => void
  onSelect: (id: string) => void
  onCreate: () => void
  onCreateAgent: () => void
  onDelete: (id: string) => void
}

const ConversationList = ({
  agents,
  conversations,
  activeId,
  onCreate,
  onCreateAgent,
  onDelete,
  onSearch,
  onSelect,
  search,
}: ConversationListProps) => {
  const agentsById = new Map(agents.map((agent) => [agent.id, agent]))

  return (
    <div className="sidebar">
      <div className="sidebar__header">
        <div className="brand-mark">
          <span className="brand-mark__icon">
            <HomeFilled />
          </span>
          <strong>AgentHub</strong>
        </div>
      </div>

      <Button className="sidebar__create" icon={<PlusOutlined />} type="primary" onClick={onCreate}>
        新建对话
      </Button>

      <Input
        allowClear
        className="conversation-search"
        placeholder="搜索对话或消息"
        prefix={<SearchOutlined />}
        suffix={<span className="search-shortcut">⌘K</span>}
        value={search}
        onChange={(event) => onSearch(event.target.value)}
      />

      <section className="sidebar__section">
        <div className="sidebar__section-title">
          <span className="sidebar__label">常用代理</span>
          <Button aria-label="添加代理" icon={<PlusOutlined />} size="small" type="text" onClick={onCreateAgent} />
        </div>
        <div className="agent-list">
          {agents.map((agent) => (
            <div className="agent-row" key={agent.id}>
              <span className="agent-row__avatar">{agent.avatar}</span>
              <div>
                <strong>{agent.name}</strong>
                <small>{agent.capabilities.slice(0, 2).join(' / ') || agent.description}</small>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="sidebar__section sidebar__section--fill">
        <div className="sidebar__section-title">
          <span className="sidebar__label">对话列表</span>
        </div>
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
                    <span className="conversation-row__top">
                      <span className="conversation-row__title">{conversation.title}</span>
                      <span className="conversation-row__time">{conversation.lastMessage ? '15:50' : '新建'}</span>
                    </span>
                    <span className="conversation-row__meta">
                      {participants.map((agent) => agent.name).join('，') || '未选择 Agent'}
                    </span>
                  </button>
                  <Popconfirm
                    cancelText="取消"
                    okText="删除"
                    title="删除这个会话？"
                    onConfirm={() => onDelete(conversation.id)}
                  >
                    <Button
                      aria-label="删除会话"
                      className="conversation-row__delete"
                      icon={<DeleteOutlined />}
                      size="small"
                      type="text"
                    />
                  </Popconfirm>
                </div>
              )
            })
          )}
        </div>
      </section>

      <div className="sidebar__footer">
        <Button icon={<SettingOutlined />} type="text">
          设置
        </Button>
        <Button icon={<ArrowRightOutlined />} type="text">
          查看全部对话
        </Button>
      </div>
    </div>
  )
}

export default ConversationList
