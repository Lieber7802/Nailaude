import {
  ArrowLeftOutlined,
  DeleteOutlined,
  PlusOutlined,
  RobotOutlined,
  SafetyCertificateOutlined,
} from '@ant-design/icons'
import { Button, Empty, Popconfirm, Tag, message as antdMessage } from 'antd'
import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AgentCreateModal from '../components/chat/AgentCreateModal'
import AgentAvatar from '../components/common/AgentAvatar'
import { agentApi, platformApi, type Agent, type AgentPlatform, type CreateAgentInput } from '../services/api'
import { useAgentStore } from '../stores/agentStore'

const AgentManage = () => {
  const navigate = useNavigate()
  const [createOpen, setCreateOpen] = useState(false)
  const [creating, setCreating] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [platforms, setPlatforms] = useState<AgentPlatform[]>([])
  const [loadingPlatforms, setLoadingPlatforms] = useState(false)
  const agents = useAgentStore((state) => state.agents)
  const loading = useAgentStore((state) => state.loading)
  const setAgents = useAgentStore((state) => state.setAgents)
  const addAgent = useAgentStore((state) => state.addAgent)
  const removeAgent = useAgentStore((state) => state.removeAgent)
  const setLoading = useAgentStore((state) => state.setLoading)
  const setError = useAgentStore((state) => state.setError)
  const builtinAgents = useMemo(() => agents.filter((agent) => agent.isBuiltin), [agents])
  const customAgents = useMemo(() => agents.filter((agent) => !agent.isBuiltin), [agents])

  useEffect(() => {
    setLoading(true)
    void agentApi
      .list()
      .then(setAgents)
      .catch((error: Error) => {
        setError(error.message)
        void antdMessage.error(error.message)
      })
      .finally(() => setLoading(false))
  }, [setAgents, setError, setLoading])

  const openCreateModal = () => {
    setCreateOpen(true)
    if (platforms.length > 0 || loadingPlatforms) return
    setLoadingPlatforms(true)
    void platformApi
      .list()
      .then(setPlatforms)
      .catch((error: Error) => {
        setError(error.message)
        void antdMessage.error(error.message)
      })
      .finally(() => setLoadingPlatforms(false))
  }

  const handleCreateAgent = async (payload: CreateAgentInput) => {
    setCreating(true)
    try {
      const agent = await agentApi.create(payload)
      addAgent(agent)
      setCreateOpen(false)
      void antdMessage.success('智能体已添加')
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '添加智能体失败'
      setError(errorMessage)
      void antdMessage.error(errorMessage)
    } finally {
      setCreating(false)
    }
  }

  const handleDeleteAgent = async (agent: Agent) => {
    if (agent.isBuiltin) return
    setDeletingId(agent.id)
    try {
      await agentApi.delete(agent.id)
      removeAgent(agent.id)
      void antdMessage.success('智能体已删除')
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '删除智能体失败'
      setError(errorMessage)
      void antdMessage.error(errorMessage)
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="agent-manage-page">
      <header className="agent-manage__header">
        <div>
          <Button icon={<ArrowLeftOutlined />} type="text" onClick={() => navigate('/workspace')}>
            返回工作台
          </Button>
          <h1>智能体管理</h1>
          <p>管理可加入对话的智能体角色。内置智能体作为系统预设保留，自定义智能体可按需删除。</p>
        </div>
        <Button icon={<PlusOutlined />} loading={loadingPlatforms} type="primary" onClick={openCreateModal}>
          新增自定义智能体
        </Button>
      </header>

      <main className="agent-manage__content">
        <section className="agent-manage__section">
          <div className="agent-manage__section-title">
            <strong>自定义智能体</strong>
            <span>{customAgents.length} 个</span>
          </div>
          {customAgents.length === 0 ? (
            <Empty description={loading ? '加载智能体中' : '暂无自定义智能体'} image={Empty.PRESENTED_IMAGE_SIMPLE} />
          ) : (
            <div className="agent-manage__grid">
              {customAgents.map((agent) => (
                <AgentManageCard
                  agent={agent}
                  deleting={deletingId === agent.id}
                  key={agent.id}
                  onDelete={() => void handleDeleteAgent(agent)}
                />
              ))}
            </div>
          )}
        </section>

        <section className="agent-manage__section">
          <div className="agent-manage__section-title">
            <strong>内置智能体</strong>
            <span>{builtinAgents.length} 个</span>
          </div>
          <div className="agent-manage__grid">
            {builtinAgents.map((agent) => (
              <AgentManageCard agent={agent} key={agent.id} />
            ))}
          </div>
        </section>
      </main>

      <AgentCreateModal
        creating={creating}
        loadingPlatforms={loadingPlatforms}
        open={createOpen}
        platforms={platforms}
        onCancel={() => setCreateOpen(false)}
        onCreate={handleCreateAgent}
      />
    </div>
  )
}

const AgentManageCard = ({
  agent,
  deleting = false,
  onDelete,
}: {
  agent: Agent
  deleting?: boolean
  onDelete?: () => void
}) => (
  <article className="agent-manage-card">
    <AgentAvatar avatar={agent.avatar} className="agent-manage-card__avatar" name={agent.name} />
    <div className="agent-manage-card__body">
      <div className="agent-manage-card__top">
        <strong>{agent.name}</strong>
        <Tag icon={agent.isBuiltin ? <SafetyCertificateOutlined /> : <RobotOutlined />}>
          {agent.isBuiltin ? '内置' : '自定义智能体'}
        </Tag>
      </div>
      <p>{agent.description || '暂无描述'}</p>
      <div className="agent-manage-card__tags">
        {agent.capabilities.length > 0 ? (
          agent.capabilities.map((capability) => <span key={capability}>{capability}</span>)
        ) : (
          <span>未设置能力标签</span>
        )}
      </div>
    </div>
    {!agent.isBuiltin && (
      <Popconfirm
        cancelText="取消"
        okText="删除"
        title="删除智能体？"
        description="删除后无法再将它加入新对话。"
        onConfirm={onDelete}
      >
        <Button
          danger
          icon={<DeleteOutlined />}
          loading={deleting}
          type="text"
        >
          删除智能体
        </Button>
      </Popconfirm>
    )}
  </article>
)

export default AgentManage
