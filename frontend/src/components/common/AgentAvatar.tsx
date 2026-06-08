interface AgentAvatarProps {
  className?: string
  name?: string
  avatar?: string
}

const isImageAvatar = (avatar?: string) =>
  Boolean(avatar && (/^https?:\/\//.test(avatar) || avatar.startsWith('/') || avatar.startsWith('data:image/')))

const AgentAvatar = ({ avatar, className = '', name }: AgentAvatarProps) => {
  const classes = ['agent-avatar', className].filter(Boolean).join(' ')
  const fallback = avatar || name?.charAt(0) || '?'

  if (isImageAvatar(avatar)) {
    return (
      <span className={classes}>
        <img alt={name ? `${name} 头像` : '智能体头像'} src={avatar} />
      </span>
    )
  }

  return <span className={classes}>{fallback}</span>
}

export default AgentAvatar
