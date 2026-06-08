import { Empty } from 'antd'
import type { Agent } from '../../services/api'
import AgentAvatar from '../common/AgentAvatar'

interface MentionSelectorProps {
  agents: Agent[]
  query: string
  visible: boolean
  onSelect: (agent: Agent) => void
}

const MentionSelector = ({ agents, onSelect, query, visible }: MentionSelectorProps) => {
  if (!visible) return null

  const normalizedQuery = query.trim().toLowerCase()
  const filteredAgents = agents.filter(
    (agent) =>
      !normalizedQuery ||
      agent.name.toLowerCase().includes(normalizedQuery) ||
      agent.capabilities.some((capability) => capability.toLowerCase().includes(normalizedQuery))
  )

  return (
    <div className="mention-selector" role="listbox">
      {filteredAgents.length === 0 ? (
        <Empty description="没有匹配的智能体" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      ) : (
        filteredAgents.map((agent) => (
          <button className="mention-selector__item" key={agent.id} type="button" onMouseDown={() => onSelect(agent)}>
            <AgentAvatar avatar={agent.avatar} className="agent-row__avatar" name={agent.name} />
            <span>
              <strong>{agent.name}</strong>
              <small>{agent.capabilities.slice(0, 2).join(' / ')}</small>
            </span>
          </button>
        ))
      )}
    </div>
  )
}

export default MentionSelector
