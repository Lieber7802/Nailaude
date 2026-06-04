import { ApiOutlined, IdcardOutlined, TagsOutlined, UserAddOutlined } from '@ant-design/icons'
import { Form, Input, Modal, Select } from 'antd'
import { useEffect, useMemo } from 'react'
import type { AgentPlatform, CreateAgentInput } from '../../services/api'

interface AgentCreateModalProps {
  creating: boolean
  open: boolean
  platforms: AgentPlatform[]
  loadingPlatforms: boolean
  onCancel: () => void
  onCreate: (input: CreateAgentInput) => Promise<void>
}

interface FormValues {
  name: string
  avatar: string
  description: string
  capabilities: string[]
  systemInstruction: string
  platformId: string
}

const DEFAULT_CAPABILITY_OPTIONS = [
  '代码生成',
  '代码审查',
  '前端',
  '后端',
  '产品',
  '需求分析',
  '文档',
  '测试',
  '架构',
]

const AgentCreateModal = ({
  creating,
  loadingPlatforms,
  onCancel,
  onCreate,
  open,
  platforms,
}: AgentCreateModalProps) => {
  const [form] = Form.useForm<FormValues>()
  const userSelectablePlatforms = useMemo(() => platforms.filter((platform) => platform.id !== 'mock'), [platforms])
  const defaultPlatformId =
    userSelectablePlatforms.find((platform) => platform.status === 'available')?.id || userSelectablePlatforms[0]?.id
  const platformOptions = userSelectablePlatforms.map((platform) => ({
    label: `${platform.name} · ${platform.status}`,
    value: platform.id,
  }))

  useEffect(() => {
    if (!open || !defaultPlatformId) return
    const currentPlatformId = form.getFieldValue('platformId')
    if (!currentPlatformId || currentPlatformId === 'mock') {
      form.setFieldValue('platformId', defaultPlatformId)
    }
  }, [defaultPlatformId, form, open])

  return (
    <Modal
      confirmLoading={creating}
      okText="添加"
      open={open}
      title="添加智能体"
      width={560}
      onCancel={onCancel}
      onOk={() => void form.submit()}
    >
      <Form
        form={form}
        initialValues={{
          avatar: 'A',
          capabilities: [],
          systemInstruction: '',
        }}
        layout="vertical"
        onFinish={(values) => {
          const payload: CreateAgentInput = {
            name: values.name.trim(),
            avatar: values.avatar.trim() || 'A',
            description: values.description.trim(),
            capabilities: values.capabilities,
            systemInstruction: values.systemInstruction.trim(),
            platformId: values.platformId as CreateAgentInput['platformId'],
          }
          void onCreate(payload).then(() => form.resetFields())
        }}
      >
        <div className="agent-form-grid">
          <Form.Item
            name="name"
            label="智能体名称"
            rules={[
              { required: true, message: '请输入智能体名称' },
              { max: 32, message: '名称最多 32 个字符' },
            ]}
          >
            <Input prefix={<UserAddOutlined />} placeholder="例如：产品经理" />
          </Form.Item>
          <Form.Item
            name="avatar"
            label="头像标识"
            rules={[{ max: 4, message: '头像标识最多 4 个字符' }]}
          >
            <Input prefix={<IdcardOutlined />} placeholder="P" />
          </Form.Item>
        </div>

        <Form.Item
          name="description"
          label="功能描述 / 角色描述"
          rules={[
            { required: true, message: '请输入角色描述' },
            { max: 240, message: '描述最多 240 个字符' },
          ]}
        >
          <Input.TextArea
            autoSize={{ minRows: 3, maxRows: 5 }}
            placeholder="描述这个智能体擅长什么、何时应该被分派任务"
          />
        </Form.Item>

        <Form.Item name="capabilities" label="能力标签">
          <Select
            mode="tags"
            options={DEFAULT_CAPABILITY_OPTIONS.map((capability) => ({ label: capability, value: capability }))}
            placeholder="输入或选择能力标签"
            prefix={<TagsOutlined />}
            tokenSeparators={[',', '，', '、']}
          />
        </Form.Item>

        <Form.Item
          name="platformId"
          label="后端平台"
          rules={[{ required: true, message: '请选择后端平台' }]}
        >
          <Select
            loading={loadingPlatforms}
            notFoundContent={loadingPlatforms ? '加载平台中' : '没有可用平台'}
            optionFilterProp="label"
            options={platformOptions}
            placeholder="选择执行平台"
            suffixIcon={<ApiOutlined />}
          />
        </Form.Item>

        <Form.Item name="systemInstruction" label="角色指令">
          <Input.TextArea
            autoSize={{ minRows: 3, maxRows: 6 }}
            placeholder="可选：补充该智能体执行任务时需要遵守的角色设定和输出偏好"
          />
        </Form.Item>
      </Form>
    </Modal>
  )
}

export default AgentCreateModal
