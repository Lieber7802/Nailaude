import { TeamOutlined } from '@ant-design/icons'
import { Empty, Form, Modal, Select } from 'antd'
import { useEffect, useMemo } from 'react'
import type { Agent } from '../../services/api'
import { getAvailableConversationAgentIds } from '../../utils/chatUi'

interface AddConversationAgentsModalProps {
  agents: Agent[]
  participantIds: string[]
  updating: boolean
  open: boolean
  onCancel: () => void
  onAdd: (agentIds: string[]) => Promise<void>
}

interface FormValues {
  agentIds: string[]
}

const AddConversationAgentsModal = ({
  agents,
  onAdd,
  onCancel,
  open,
  participantIds,
  updating,
}: AddConversationAgentsModalProps) => {
  const [form] = Form.useForm<FormValues>()
  const availableAgentIds = useMemo(
    () => getAvailableConversationAgentIds(agents, participantIds),
    [agents, participantIds]
  )
  const availableAgentIdSet = useMemo(() => new Set(availableAgentIds), [availableAgentIds])
  const availableAgents = agents.filter((agent) => availableAgentIdSet.has(agent.id))

  useEffect(() => {
    if (open) {
      form.resetFields()
    }
  }, [form, open])

  return (
    <Modal
      confirmLoading={updating}
      okButtonProps={{ disabled: availableAgents.length === 0 }}
      okText="添加到对话"
      open={open}
      title="添加已有智能体"
      width={520}
      onCancel={onCancel}
      onOk={() => void form.submit()}
    >
      {availableAgents.length === 0 ? (
        <Empty description="所有智能体都已在当前对话中" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      ) : (
        <Form
          form={form}
          initialValues={{ agentIds: [] }}
          layout="vertical"
          onFinish={(values) => {
            void onAdd(values.agentIds).then(() => form.resetFields())
          }}
        >
          <Form.Item
            name="agentIds"
            label="选择要加入当前对话的智能体"
            rules={[{ required: true, message: '请选择至少一个智能体' }]}
          >
            <Select
              mode="multiple"
              optionFilterProp="label"
              options={availableAgents.map((agent) => ({
                label: `${agent.name} · ${agent.capabilities.slice(0, 2).join(' / ') || agent.description}`,
                value: agent.id,
              }))}
              placeholder="从已有智能体中选择"
              suffixIcon={<TeamOutlined />}
            />
          </Form.Item>
        </Form>
      )}
    </Modal>
  )
}

export default AddConversationAgentsModal
