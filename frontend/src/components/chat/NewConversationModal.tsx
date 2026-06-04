import { FolderOpenOutlined, TeamOutlined, UserOutlined } from '@ant-design/icons'
import { Form, Input, Modal, Radio, Select } from 'antd'
import type { Agent, CreateConversationInput } from '../../services/api'

interface NewConversationModalProps {
  agents: Agent[]
  open: boolean
  creating: boolean
  onCancel: () => void
  onCreate: (input: CreateConversationInput) => Promise<void>
}

interface FormValues {
  title: string
  type: 'single' | 'group'
  workDir: string
  participantIds: string | string[]
}

const NewConversationModal = ({ agents, creating, onCancel, onCreate, open }: NewConversationModalProps) => {
  const [form] = Form.useForm<FormValues>()
  const selectedType = Form.useWatch('type', form) || 'single'

  return (
    <Modal
      confirmLoading={creating}
      okText="创建"
      open={open}
      title="新建对话"
      onCancel={onCancel}
      onOk={() => void form.submit()}
    >
      <Form
        form={form}
        initialValues={{ type: 'single', workDir: '', participantIds: [] }}
        layout="vertical"
        onFinish={(values) => {
          const rawParticipantIds = Array.isArray(values.participantIds)
            ? values.participantIds
            : [values.participantIds]
          const participantIds = values.type === 'single' ? rawParticipantIds.slice(0, 1) : rawParticipantIds
          const payload: CreateConversationInput = {
            title: values.title || (values.type === 'group' ? '新的群聊' : '新的单聊'),
            type: values.type,
            workDir: values.workDir,
            participantIds,
          }
          void onCreate(payload).then(() => form.resetFields())
        }}
      >
        <Form.Item name="type" label="对话类型">
          <Radio.Group>
            <Radio.Button value="single">
              <UserOutlined /> 单聊
            </Radio.Button>
            <Radio.Button value="group">
              <TeamOutlined /> 群聊
            </Radio.Button>
          </Radio.Group>
        </Form.Item>
        <Form.Item name="title" label="标题">
          <Input placeholder="例如：Todo App 开发" />
        </Form.Item>
        <Form.Item
          name="participantIds"
          label="参与智能体"
          rules={[{ required: true, message: '请选择至少一个智能体' }]}
        >
          <Select
            mode={selectedType === 'group' ? 'multiple' : undefined}
            optionFilterProp="label"
            options={agents.map((agent) => ({
              label: `${agent.name} · ${agent.capabilities.slice(0, 2).join(' / ')}`,
              value: agent.id,
            }))}
            placeholder="选择智能体"
          />
        </Form.Item>
        <Form.Item
          name="workDir"
          label="工作目录（留空自动生成）"
        >
          <Input prefix={<FolderOpenOutlined />} placeholder="留空自动生成，或手动输入 workspaces/xxx" />
        </Form.Item>
      </Form>
    </Modal>
  )
}

export default NewConversationModal
