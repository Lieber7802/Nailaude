import { ApiOutlined, ReloadOutlined, TagsOutlined, UploadOutlined, UserAddOutlined } from '@ant-design/icons'
import { Button, Form, Input, Modal, Select } from 'antd'
import type { ChangeEvent } from 'react'
import { useEffect, useMemo, useRef, useState } from 'react'
import type { AgentPlatform, CreateAgentInput } from '../../services/api'
import AgentAvatar from '../common/AgentAvatar'

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

const DEFAULT_CUSTOM_AGENT_AVATAR = '/agent-avatars/default_custom_agent.png'
const AVATAR_IMAGE_SIZE = 256

const readAvatarFile = (file: File): Promise<string> =>
  new Promise((resolve, reject) => {
    const objectUrl = URL.createObjectURL(file)
    const image = new Image()

    image.onload = () => {
      const canvas = document.createElement('canvas')
      const size = Math.min(image.naturalWidth, image.naturalHeight)
      const sourceX = (image.naturalWidth - size) / 2
      const sourceY = (image.naturalHeight - size) / 2

      canvas.width = AVATAR_IMAGE_SIZE
      canvas.height = AVATAR_IMAGE_SIZE
      canvas.getContext('2d')?.drawImage(image, sourceX, sourceY, size, size, 0, 0, AVATAR_IMAGE_SIZE, AVATAR_IMAGE_SIZE)
      URL.revokeObjectURL(objectUrl)
      resolve(canvas.toDataURL('image/png'))
    }

    image.onerror = () => {
      URL.revokeObjectURL(objectUrl)
      reject(new Error('图片读取失败'))
    }

    image.src = objectUrl
  })

const AgentCreateModal = ({
  creating,
  loadingPlatforms,
  onCancel,
  onCreate,
  open,
  platforms,
}: AgentCreateModalProps) => {
  const [form] = Form.useForm<FormValues>()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [avatarError, setAvatarError] = useState('')
  const avatarValue = Form.useWatch('avatar', form) || DEFAULT_CUSTOM_AGENT_AVATAR
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

  const handleAvatarUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file) return

    if (!file.type.startsWith('image/')) {
      setAvatarError('请选择图片文件')
      return
    }

    try {
      const avatarDataUrl = await readAvatarFile(file)
      form.setFieldValue('avatar', avatarDataUrl)
      setAvatarError('')
    } catch {
      setAvatarError('头像图片读取失败，请换一张图片重试')
    }
  }

  const resetAvatar = () => {
    form.setFieldValue('avatar', DEFAULT_CUSTOM_AGENT_AVATAR)
    setAvatarError('')
  }

  return (
    <Modal
      confirmLoading={creating}
      okText="创建"
      open={open}
      title="新增自定义智能体"
      width={560}
      onCancel={onCancel}
      onOk={() => void form.submit()}
    >
      <Form
        form={form}
        initialValues={{
          avatar: DEFAULT_CUSTOM_AGENT_AVATAR,
          capabilities: [],
          systemInstruction: '',
        }}
        layout="vertical"
        onFinish={(values) => {
          const payload: CreateAgentInput = {
            name: values.name.trim(),
            avatar: values.avatar.trim() || DEFAULT_CUSTOM_AGENT_AVATAR,
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
          <div className="agent-avatar-field">
            <span className="agent-avatar-field__label">头像标识</span>
            <Form.Item name="avatar" noStyle rules={[{ required: true, message: '请选择头像' }]}>
              <Input type="hidden" />
            </Form.Item>
            <div className="agent-avatar-picker">
              <AgentAvatar avatar={avatarValue} className="agent-avatar-picker__preview" name="自定义智能体" />
              <div className="agent-avatar-picker__actions">
                <Button htmlType="button" icon={<UploadOutlined />} onClick={() => fileInputRef.current?.click()}>
                  上传图片
                </Button>
                <Button htmlType="button" icon={<ReloadOutlined />} onClick={resetAvatar}>
                  恢复默认
                </Button>
              </div>
              <input
                accept="image/*"
                aria-label="上传智能体头像"
                className="agent-avatar-picker__input"
                ref={fileInputRef}
                type="file"
                onChange={handleAvatarUpload}
              />
              {avatarError && <span className="agent-avatar-picker__error">{avatarError}</span>}
            </div>
          </div>
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
