interface AgentAvatarProps {
  name?: string
  avatar?: string
}

const AgentAvatar = ({ name, avatar }: AgentAvatarProps) => {
  return <span className="agent-avatar">{avatar || name?.charAt(0) || '?'}</span>
}

export default AgentAvatar
